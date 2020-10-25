import pandas as pd
import numpy

from app.serotracker_sqlalchemy import db_session, AirtableSource, db_model_config
from sqlalchemy import case, and_


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
                     AirtableSource.isotype_iga == 'false'), 'IgM')
                ],
                else_='').label("isotypes")
    return expression


def _get_parsed_record(results):
    # Store columns that are multi select and that need to be converted to list
    multi_select_cols = db_model_config['multi_select_columns']
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
    with db_session() as session:
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
            table_infos = db_model_config['supplementary_table_info']

            # Add columns from supplementary tables and add isotype col expression
            for sup_table in table_infos:
                fields_list.append(getattr(sup_table['main_table'], f"{sup_table['entity']}_name").label(sup_table['entity']))

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
                result = _get_parsed_record(result)
        except Exception as e:
            print(e)
    return result


def get_country_seroprev_summaries(records):
    # Turn records into df and remove list from country
    records_df = pd.DataFrame(records)

    # Get unique list of countries
    countries = records_df.country.unique()
    study_counts_list = []

    # For each country, create a payload with all the seroprev summary info
    for country in countries:
        country_seroprev_summary_dict = {}
        country_seroprev_summary_dict['country'] = country
        records_for_country = records_df[records_df['country'] == country]

        # Get total number of seroprev estimates in country
        country_seroprev_summary_dict['n_estimates'] = records_for_country.shape[0]

        # Get total number of tests administered in country
        country_seroprev_summary_dict['n_tests_administered'] = int(records_for_country.denominator_value.sum())

        # Summarize seroprev estimate info at each estimate grade level
        estimate_grades = ['National', 'Regional', 'Local', 'Sublocal']
        grades_seroprev_summaries_dict = {}
        for grade in estimate_grades:
            estimate_grade_dict = {}
            records_for_grade = records_for_country[records_for_country['estimate_grade'] == grade]
            n_estimates = records_for_grade.shape[0]

            if n_estimates == 0:
                estimate_grade_dict['n_estimates'] = 0
                estimate_grade_dict['min_estimate'] = None
                estimate_grade_dict['max_estimate'] = None
            else:
                # Add number of estimates for that grade
                estimate_grade_dict['n_estimates'] = n_estimates

                # Add min and max seroprev estimates
                estimate_grade_dict['min_estimate'] = records_for_grade.serum_pos_prevalence.min()
                estimate_grade_dict['max_estimate'] = records_for_grade.serum_pos_prevalence.max()
            grades_seroprev_summaries_dict[grade] = estimate_grade_dict
        country_seroprev_summary_dict['seroprevalence_estimate_summary'] = grades_seroprev_summaries_dict
        study_counts_list.append(country_seroprev_summary_dict)
    return study_counts_list
