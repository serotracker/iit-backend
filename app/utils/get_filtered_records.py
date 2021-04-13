from itertools import groupby
from functools import reduce
from app.serotracker_sqlalchemy import db_session, DashboardSource, ResearchSource, \
    db_model_config, Country, State, City, dashboard_source_cols, research_source_cols
import pandas as pd
import numpy as np
from app.utils.estimate_prioritization import get_prioritized_estimates
from statistics import mean
from typing import List, Dict, Any


def get_all_records(research_fields=False):
    with db_session() as session:
        # Get all records for now, join on all tables
        table_infos = db_model_config['supplementary_table_info']

        # Create list of entity_name keys such as "age_name" which would be "Youth (13-17)"
        entity_names = [f"{t['entity']}" for t in table_infos]
        entity_names += ['country_latitude', 'country_longitude', 'city_longitude', 'city_latitude',
                         'state_longitude', 'state_latitude']

        # Add columns from dashboard source to select statement
        fields_list = [DashboardSource.source_id]
        for field_string in dashboard_source_cols:
            fields_list.append(getattr(DashboardSource, field_string))

        # If research fields is True, add columns from research source to select statement
        if research_fields:
            for col in research_source_cols:
                fields_list.append(getattr(ResearchSource, col))

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

        # If research fields is true, join to research source table
        if research_fields:
            query = query.join(ResearchSource, ResearchSource.source_id == DashboardSource.source_id)

        query = query.all()
        query_dict = [q._asdict() for q in query]

        # Merge entities of the same entry into a single set of entity values
        # e.g., ["Youth (13-17)", "Children (0-12)"]
        def reduce_entities(a, b):
            for entity in entity_names:
                if not a[entity]:
                    a[entity] = []
                elif isinstance(a[entity], str) or isinstance(a[entity], float):
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


def get_filtered_records(research_fields=False, filters=None, columns=None,
                         sampling_start_date=None, sampling_end_date=None,
                         publication_start_date=None, publication_end_date=None, prioritize_estimates=True,
                         prioritize_estimates_mode='dashboard', include_in_srma=False):
    query_dicts = get_all_records(research_fields)
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

    def date_filter(record, start_date=None, end_date=None, use_sampling_date=True):
        status = True
        record_end_date = record["sampling_end_date"] if use_sampling_date else record["publication_date"]

        # Filter the sampling end date or publication date by start and/or end date bounds
        if start_date is not None:
            status = status and record_end_date and record_end_date >= start_date
        if end_date is not None:
            status = status and record_end_date and record_end_date <= end_date
        return status

    result = list(filter(lambda x: date_filter(x, start_date=sampling_start_date,
                                               end_date=sampling_end_date, use_sampling_date=True), result))
    result = list(filter(lambda x: date_filter(x, start_date=publication_start_date,
                                               end_date=publication_end_date, use_sampling_date=False), result))

    # Format dates after date filter has been applied
    for record in result:
        isoformat_fields =\
            ['sampling_end_date', 'sampling_start_date', 'publication_date', 'date_created', 'last_modified_time']
        for field in isoformat_fields:
            if record.get(field, None) is not None:
                record[field] = record[field].isoformat()

    # TODO: Determine whether to update get_prioritized_estimates to work on dictionaries
    # or keep everything in dataframes (don't want to have this conversion here long term)
    if prioritize_estimates:
        result_df = pd.DataFrame(result)
        prioritized_records = get_prioritized_estimates(result_df, mode=prioritize_estimates_mode)
        # If records exist, clean dataframe
        if not prioritized_records.empty:
            # Convert from True/None to True/False
            # TODO: maybe this is something we enforce in the ETL moving fwd
            for col in prioritized_records.columns:
                # Note purpose of this line is to check if the col in question is a boolean col
                # Can't simply check the dtype because cols with True/None instead of
                # True/False have dtype="object" instead of "bool"
                if True in prioritized_records[col].values:
                    prioritized_records[col] = prioritized_records[col].fillna(False)
            # Filling all NaN values with None: https://stackoverflow.com/questions/46283312/how-to-proceed-with-none-value-in-pandas-fillna
            prioritized_records = prioritized_records.fillna(np.nan).replace({np.nan: None})
        result = prioritized_records.to_dict('records')

    # Need to check if 'research_fields' is applied
    # because the include_in_srma field is in the ResearchSource table
    if include_in_srma and research_fields:
        result = [estimate for estimate in result if estimate['include_in_srma']]

    for record in result:
        # Get the latitude and longitude to use for estimate pin
        # Use coordinate at the most specific geographic level that's available in the database
        # If there are multiple coordinates for a given geographic level, use the average
        # Note this needs to happen after prioritization of estimates
        # because the prioritization function may group multiple estimates from the same study into 1
        region_types = ['country', 'state', 'city']
        for region_type in region_types:
            if len(record[f'{region_type}_latitude']) == 0:
                # Edge case for when there isn't even a country level coordinate
                if 'pin_latitude' not in record:
                    record['pin_latitude'] = None
                    record['pin_longitude'] = None
                    record['pin_region_type'] = ''
                break
            # If we find multiple coordinates for a given geographic level
            # Average them and use that average to render the pin
            else:
                record['pin_latitude'] = mean(record[f'{region_type}_latitude'])
                record['pin_longitude'] = mean(record[f'{region_type}_longitude'])
                record['pin_region_type'] = region_type

        # Delete lng/lat columns that are now unnecessary
        for region_type in region_types:
            record.pop(f'{region_type}_latitude')
            record.pop(f'{region_type}_longitude')

    # Finally, if columns have been supplied, only return those columns
    if columns is not None and len(columns) > 0:
        def grab_cols(result, columns):
            ret = {}
            for col in columns:
                ret[col] = result.get(col)
            return ret

        result = [grab_cols(i, columns) for i in result]
    return result

'''Gets and returns a dictionary of pages of records

:param records: list of unpaginated records
:param min_page_index: minimum page index
:param max_page_index: maximum page index
:param per_page: number of records per page
:param reverse: whether to sort list of unpaginated records in reverse order or not 
:param sorting_key: key by which list of unpaginated records are sorted
:returns a dictionary of lists of records (len(list) == per_page)
'''
def get_paginated_records(records: List[Dict[str, Any]], min_page_index: int, max_page_index: int, per_page: int = 5, reverse: bool = False, sorting_key: str = "sampling_end_date") -> Dict[int, List[Dict[str, Any]]]:
    # Order the records first
    sorted_records = sorted(records, key=lambda x: (x[sorting_key] is None, x[sorting_key]), reverse=reverse)

    # Input is non-zero indexing, but we map to zero indexing (e.g. input 1-3 maps to 0-2) but we still return non-zero indexing
    min_page_index -= 1
    max_page_index -= 1

    # Create dictionary of pages of records
    return {i+1:sorted_records[i*per_page:i*per_page+per_page]
            if i * per_page + per_page < len(sorted_records)
            else sorted_records[i*per_page:]
            for i in range(min_page_index, max_page_index + 1)}
