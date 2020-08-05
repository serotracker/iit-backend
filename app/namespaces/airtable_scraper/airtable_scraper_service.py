import os

import pandas as pd
import numpy

from app.serotracker_sqlalchemy import db_session, AirtableSource, Age, PopulationGroup, TestManufacturer, \
    ApprovingRegulator, TestType, AgeBridge, PopulationGroupBridge, \
    TestManufacturerBridge, ApprovingRegulatorBridge, TestTypeBridge
from sqlalchemy import create_engine, case, and_


def _get_engine():
    # Create engine to connect to whiteclaw database
    engine = create_engine('postgresql://{username}:{password}@localhost/whiteclaw'.format(
        username=os.getenv('DATABASE_USERNAME'),
        password=os.getenv('DATABASE_PASSWORD')))
    return engine


def _get_isotype_col_expression():
    expression = case(
                [
                    (and_(AirtableSource.isotype_igg == 'true',
                     AirtableSource.isotype_igm == 'true',
                     AirtableSource.isotype_iga == 'true'), 'IgG, IgM, IgA'),
                    (and_(AirtableSource.isotype_igg == 'true',
                     AirtableSource.isotype_igm == 'false',
                     AirtableSource.isotype_iga == 'true'), 'IgG, IgA'),
                    (and_(AirtableSource.isotype_igg == 'true',
                     AirtableSource.isotype_igm == 'true',
                     AirtableSource.isotype_iga == 'false'), 'IgG, IgM'),
                    (and_(AirtableSource.isotype_igg == 'false',
                     AirtableSource.isotype_igm == 'true',
                     AirtableSource.isotype_iga == 'true'), 'IgM, IgA'),
                    (and_(AirtableSource.isotype_igg == 'true',
                     AirtableSource.isotype_igm == 'false',
                     AirtableSource.isotype_iga == 'false'), 'IgG'),
                    (and_(AirtableSource.isotype_igg == 'false',
                     AirtableSource.isotype_igm == 'false',
                     AirtableSource.isotype_iga == 'true'), 'IgA'),
                    (and_(AirtableSource.isotype_igg == 'false',
                     AirtableSource.isotype_igm == 'true',
                     AirtableSource.isotype_iga == 'false'), 'IgM')], else_='').label("isotypes")
    return expression


def _get_parsed_record(results):
    # Store columns that are multi select and that need to be converted to list
    multi_select_cols = ['age_name', 'population_group_name', 'test_manufacturer_name',
                         'approving_regulator_name', 'test_type_name']
    results_df = pd.DataFrame(results)

    # Create one dictionary of record details to return
    record_details = {}
    for col in results_df.columns:
        # Convert multi select values into an array
        if col in multi_select_cols:
            multi_select_vals = list(set(getattr(results_df, col).tolist()))
            record_details[col] = multi_select_vals

        # Convert comma sep string of isotypes to list
        elif col == 'isotypes':
            isotypes = results_df.iloc[0][col]
            if isotypes:
                record_details[col] = isotypes.split(',')
            else:
                record_details[col] = []

        # Otherwise just return the single value of the column
        else:
            record_details[col] = results_df.iloc[0][col]

        # Convert to float or int if numpy - otherwise cannot jsonify endpoint return result
        if isinstance(record_details[col], numpy.float64):
            record_details[col] = float(record_details[col])

        if isinstance(record_details[col], numpy.int64):
            record_details[col] = int(record_details[col])
    return record_details


def get_record_details(source_id):
    engine = _get_engine()
    with db_session(engine) as session:
        try:
            # Construct case when expression to generate isotype column based on isotype bool cols
            isotype_case_expression = _get_isotype_col_expression()

            # Store list of airtable source columns to pull
            airtable_source_cols = ['source_id',
                                    'source_name',
                                    'summary',
                                    'study_status',
                                    'sex',
                                    'serum_pos_prevalence',
                                    'denominator_value',
                                    'overall_risk_of_bias',
                                    'sampling_method',
                                    'sampling_start_date',
                                    'sampling_end_date',
                                    'country',
                                    'sensitivity',
                                    'specificity']

            # Build list of columns to use in query starting with airtable source columns
            fields_list = []
            for col in airtable_source_cols:
                fields_list.append(getattr(AirtableSource, col))

            # Store info about supplementary tables to join to airtable source
            table_infos = [
                {
                    "bridge_table": AgeBridge,
                    "main_table": Age,
                    "entity": "age"
                },
                {
                    "bridge_table": PopulationGroupBridge,
                    "main_table": PopulationGroup,
                    "entity": "population_group"
                },
                {
                    "bridge_table": TestManufacturerBridge,
                    "main_table": TestManufacturer,
                    "entity": "test_manufacturer"
                },
                {
                    "bridge_table": ApprovingRegulatorBridge,
                    "main_table": ApprovingRegulator,
                    "entity": "approving_regulator"
                },
                {
                    "bridge_table": TestTypeBridge,
                    "main_table": TestType,
                    "entity": "test_type"
                }
            ]

            # Add columns from supplementary tables and add isotype col expression
            for sup_table in table_infos:
                fields_list.append(getattr(sup_table['main_table'], f"{sup_table['entity']}_name"))

            query = session.query(*fields_list, isotype_case_expression)

            # Build query to join supplementary tables to airtable source
            for sup_table in table_infos:
                main_table = sup_table['main_table']
                bridge_table = sup_table['bridge_table']
                entity_id = f"{sup_table['entity']}_id"
                query = query.outerjoin(bridge_table, bridge_table.source_id == AirtableSource.source_id)\
                    .outerjoin(main_table, getattr(bridge_table, entity_id) == getattr(main_table, entity_id))

            # Filter by input source id and convert results to dicts
            query = query.filter(AirtableSource.source_id == source_id)
            result = query.all()
            result = [x._asdict() for x in result]

            # If multiple records are returned, parse results to return one record
            if len(result) > 1:
                record = _get_parsed_record(result)
        except Exception as e:
            print(e)
    return record

