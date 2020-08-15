import os

from app.serotracker_sqlalchemy import db_session, AirtableSource, db_model_config
from sqlalchemy import create_engine
from itertools import groupby
from functools import reduce

# Create engine to connect to whiteclaw database
engine = create_engine('postgresql://{username}:{password}@{host}/whiteclaw'.format(
    username=os.getenv('DATABASE_USERNAME'),
    password=os.getenv('DATABASE_PASSWORD'),
    host=os.getenv('DATABASE_HOST')))


def get_all_records(columns=None):
    with db_session(engine) as session:
        # Get all records for now, join on all tables
        table_infos = db_model_config['supplementary_table_info']

        # Create list of entity_name keys such as "age_name" which would be "Youth (13-17)"
        entity_names = [f"{t['entity']}_name" for t in table_infos if (columns is None or t['entity'] in columns)]

        # Create list of fields in AirtableSource to query unless the specific columns are specified
        field_strings = ['source_name', 'source_type', 'study_status', 'country', 'denominator_value',
                         'overall_risk_of_bias', 'serum_pos_prevalence', 'isotype_igm', 'isotype_iga',
                         'isotype_igg', 'sex', 'sampling_end_date', 'estimate_grade']

        # If columns are specified, just take the field strings from the Airtable Source table that are in columns
        if columns is not None:
            field_strings = [i for i in field_strings if i in columns or (any("isotype" in s for s in columns)
                                                                          and "isotype" in i)]
        fields_list = [AirtableSource.source_id]
        for field_string in field_strings:
            fields_list.append(getattr(AirtableSource, field_string))

        for table_info in table_infos:
            # If columns are specified, only table bridge table fields in the columns list
            if columns is not None:
                if table_info['entity'] in columns:
                    fields_list.append(getattr(table_info["main_table"], f"{table_info['entity']}_name"))
            else:
                fields_list.append(getattr(table_info["main_table"], f"{table_info['entity']}_name"))

        query = session.query(*fields_list)

        # There are entries that have multiple field values for a certain entity
        # e.g., an entry may be associated with two different age groups, "Youth (13-17)" and "Children (0-12)"
        # Gather up all of these rows
        for table_info in table_infos:
            # If columns are specified, only join bridge tables with linking fields in the columns list
            if columns is not None:
                if table_info['entity'] not in columns:
                    continue
            bridge_table = table_info["bridge_table"]
            main_table = table_info["main_table"]
            entity = f"{table_info['entity']}_id"
            try:
                query = query.join(bridge_table, getattr(bridge_table, "source_id") ==
                                   AirtableSource.source_id, isouter=True) \
                    .join(main_table, getattr(main_table, entity) == getattr(bridge_table, entity), isouter=True)
            except Exception as e:
                print(e)
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
                for entity in entity_names:
                    record[entity] = [record[entity]] if record[entity] is not None else []
                processed_record = record
            else:
                processed_record = reduce(reduce_entities, record_list)

            processed_record['isotypes_reported'] = []
            isotype_mapping = {'isotype_igm': 'IgM', 'isotype_iga': 'IgA', 'isotype_igg': 'IgG'}

            for k, v in isotype_mapping.items():
                if processed_record[k]:
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
  'age_name' : {'Youth (13-17)', 'All'},
  'country' : {'United States'}
}

Output: set of records represented by dicts
'''


def get_filtered_records(filters=None, columns=None, start_date=None, end_date=None):
    query_dicts = get_all_records(columns)
    if query_dicts is None or len(query_dicts) == 0:
        return []

    result = []

    # Return all records if no filters are passed in
    if filters:
        def should_include(d, k, v):
            if isinstance(d[k], str) and d[k] in v:
                return True
            elif isinstance(d[k], list) and set(d[k]).intersection(set(v)):
                return True
            return False

        for k, v in filters.items():
            # Add records passing the first filter
            if not result:
                for d in query_dicts:
                    if should_include(d, k, v):
                        result.append(d)
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

    return result


'''
Note: `page_index` is zero-indexed here!
'''


def get_paginated_records(query_dicts, sorting_key='source_id', page_index=0, per_page=10, reverse=False):
    sorting_key = sorting_key or 'source_id'
    page_index = page_index or 0
    per_page = per_page or 10
    reverse = reverse or False

    # Order the records first
    sorted_records = sorted(query_dicts, key=lambda x: (x[sorting_key] is None, x[sorting_key]), reverse=reverse)

    start = page_index * per_page
    end = page_index * per_page + per_page

    return sorted_records[start:end]
