from itertools import groupby
from functools import reduce
from app.serotracker_sqlalchemy import db_session, DashboardSource, db_model_config, Country, State, City
import pandas as pd
import numpy as np
from .estimate_prioritization import get_prioritized_estimates


def get_all_records():
    with db_session() as session:
        # Get all records for now, join on all tables
        table_infos = db_model_config['supplementary_table_info']

        # Create list of entity_name keys such as "age_name" which would be "Youth (13-17)"
        entity_names = [f"{t['entity']}" for t in table_infos]

        # Create list of fields in DashboardSource to query unless the specific columns are specified
        field_strings = ['source_name', 'source_type', 'study_name', 'denominator_value',
                         'overall_risk_of_bias', 'serum_pos_prevalence', 'isotype_igm', 'isotype_iga',
                         'isotype_igg', 'sex', 'age', 'sampling_start_date', 'sampling_end_date', 'estimate_grade',
                         'isotype_comb', 'academic_primary_estimate', 'dashboard_primary_estimate', 'pop_adj',
                         'test_adj', 'specimen_type', 'test_type', 'population_group', 'url']

        fields_list = [DashboardSource.source_id]
        for field_string in field_strings:
            fields_list.append(getattr(DashboardSource, field_string))

        for table_info in table_infos:
            # The label method returns an alias for the column being queried
            # Use case: We want to get fields from the bridge table without the _name suffix
            fields_list.append(getattr(table_info["main_table"], f"{table_info['entity']}_name").label(
                table_info['entity']))

        # Alias for country name and iso3 code
        fields_list.append(Country.country_name.label("country"))
        fields_list.append(Country.country_iso3.label("country_iso3"))
        # Aliases for lat lngs
        fields_list.append(Country.latitude.label("country_latitude"))
        fields_list.append(Country.longitude.label("country_longitude"))
        fields_list.append(State.latitude.label("state_latitude"))
        fields_list.append(State.longitude.label("state_longitude"))
        fields_list.append(City.latitude.label("city_latitude"))
        fields_list.append(City.longitude.label("city_longitude"))

        query = session.query(*fields_list)

        # There are entries that have multiple field values for a certain entity
        # e.g., an entry may be associated with two different age groups, "Youth (13-17)" and "Children (0-12)"
        # Gather up all of these rows
        for table_info in table_infos:
            bridge_table = table_info["bridge_table"]
            main_table = table_info["main_table"]
            entity = f"{table_info['entity']}_id"
            try:
                query = query.join(bridge_table, getattr(bridge_table, "source_id") ==
                                   DashboardSource.source_id, isouter=True) \
                    .join(main_table, getattr(main_table, entity) == getattr(bridge_table, entity), isouter=True)
            except Exception as e:
                print(e)
        # Join on country table
        query = query.join(Country, Country.country_id == DashboardSource.country_id, isouter=True)
        query = query.all()
        query_dict = [q._asdict() for q in query]

        # Merge entities of the same entry into a single set of entity values
        # e.g., ["Youth (13-17)", "Children (0-12)"]
        def reduce_entities(a, b):
            for entity in entity_names:
                if not a[entity]:
                    a[entity] = []
                elif isinstance(a[entity], str):
                    a[entity] = [a[entity]]
                if b[entity] is not None and b[entity] not in a[entity]:
                    a[entity].append(b[entity])
            return a

        # Reduce entities for every entity_name key that we selected
        def process_record(record_list):
            if len(record_list) == 1:
                record = record_list[0]
                if entity_names:
                    for entity in entity_names:
                        record[entity] = [record[entity]] if record[entity] is not None else []
                processed_record = record
            else:
                processed_record = reduce(reduce_entities, record_list)

            # Get the latitude and longitude to use for estimate pin
            # Use the most specific one that's available in the database
            # This seems to be more robust for now than relying on estimate grades
            # E.g. not always sure if Local = city or Local = state (since sometimes Local = 3/4 cities)
            region_types = ['city', 'state', 'country']
            for region_type in region_types:
                processed_record['pin_latitude'] = processed_record[f'{region_type}_latitude']
                processed_record['pin_longitude'] = processed_record[f'{region_type}_longitude']
                processed_record['pin_region_type'] = region_type
                if processed_record['pin_latitude'] is not None and processed_record['pin_longitude'] is not None:
                    break
            # Delete lng/lat columns that are now unnecessary
            for region_type in region_types:
                processed_record.pop(f'{region_type}_latitude')
                processed_record.pop(f'{region_type}_longitude')

            # Format isotypes reported column
            processed_record['isotypes_reported'] = []
            isotype_mapping = {'isotype_igm': 'IgM', 'isotype_iga': 'IgA', 'isotype_igg': 'IgG'}

            for k, v in isotype_mapping.items():
                # Need to check if true here, not "not None"
                if processed_record.get(k, None):
                    processed_record['isotypes_reported'].append(v)
                processed_record.pop(k, None)

            return processed_record

        # `query_dicts` is a list of rows (represented as dicts) with unique source_id and lists of 
        # their associated entities 
        query_dicts = [process_record(list(group)) for _, group in groupby(query_dict, key=lambda x: x["source_id"])]
        return query_dicts


'''
Filter are in the following format: 
{ 
  'age' : ['Youth (13-17)', 'All'],
  'country' : ['United States']
}

Output: set of records represented by dicts
'''


def get_filtered_records(filters=None, columns=None, start_date=None, end_date=None, prioritize_estimates=True):
    query_dicts = get_all_records()
    if query_dicts is None or len(query_dicts) == 0:
        return []

    result = []

    # Return all records if no filters are passed in
    if filters:
        def should_include(d, k, v):
            if len(v) == 0:
                return True
            elif isinstance(d[k], str) and d[k] in v:
                return True
            elif isinstance(d[k], list) and set(d[k]).intersection(set(v)):
                return True
            return False

        applied_filter = False
        for k, v in filters.items():
            # Add records passing the first filter
            if not applied_filter:
                for d in query_dicts:
                    if should_include(d, k, v):
                        result.append(d)
                applied_filter = True
                continue

            result = list(filter(lambda x: should_include(x, k, v), result))

    else:
        result = query_dicts

    def date_filter(record, start_date=None, end_date=None):
        status = True

        if start_date is not None:
            status = status and record["sampling_end_date"] and start_date <= record["sampling_end_date"]
        if end_date is not None:
            status = status and record["sampling_end_date"] and end_date >= record["sampling_end_date"]
        return status

    result = list(filter(lambda x: date_filter(x, start_date=start_date, end_date=end_date), result))

    # Format dates after date filter has been applied
    for record in result:
        if record['sampling_end_date'] is not None:
            record['sampling_end_date'] = record['sampling_end_date'].isoformat()
        if record['sampling_start_date'] is not None:
            record['sampling_start_date'] = record['sampling_start_date'].isoformat()

    # TODO: Determine whether to update get_prioritized_estimates to work on dictionaries
    # or keep everything in dataframes (don't want to have this conversion here long term)
    if prioritize_estimates:
        result_df = pd.DataFrame(result)
        prioritized_records = get_prioritized_estimates(result_df, mode="dashboard")
        if not prioritized_records.empty:
            # Filling all NaN values with None: https://stackoverflow.com/questions/46283312/how-to-proceed-with-none-value-in-pandas-fillna
            prioritized_records = prioritized_records.fillna(np.nan).replace({np.nan: None})
        result = prioritized_records.to_dict('records')

    # Finally, if columns have been supplied, only return those columns
    if columns is not None and len(columns) > 0:
        def grab_cols(result, columns):
            ret = {}
            for col in columns:
                ret[col] = result.get(col)
            return ret

        result = [grab_cols(i, columns) for i in result]
    return result

'''
Note: `page_index` is zero-indexed here!
'''


def get_paginated_records(query_dicts, sorting_key, page_index, per_page, reverse):
    # Order the records first
    sorted_records = sorted(query_dicts, key=lambda x: (x[sorting_key] is None, x[sorting_key]), reverse=reverse)

    start = page_index * per_page
    end = page_index * per_page + per_page

    return sorted_records[start:end]
