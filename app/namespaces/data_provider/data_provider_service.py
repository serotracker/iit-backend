from app.serotracker_sqlalchemy.models import PopulationGroupOptions
import pandas as pd
import numpy
import math
from random import uniform
from typing import Dict, Any

from app.serotracker_sqlalchemy import db_session, DashboardSource, Country, ResearchSource, State, City, \
    AntibodyTarget, db_model_config, dashboard_source_cols
from app.utils import _get_isotype_col_expression
from sqlalchemy import distinct, func
from app.database_etl.postgres_tables_handler import get_filter_static_options


def _get_parsed_record(results):
    # Store columns that are multi select and that need to be converted to list
    multi_select_cols = db_model_config['multi_select_columns']
    results_df = pd.DataFrame(results)

    # Create one dictionary of record details to return
    record_details = {}
    for col in results_df.columns:
        # Convert multi select values into an array
        if col in multi_select_cols:
            multi_select_vals = [e for e in list(set(getattr(results_df, col).tolist())) if e is not None]
            record_details[col] = multi_select_vals

        # Otherwise just return the single value of the column
        else:
            record_details[col] = results_df.iloc[0][col]

        # Convert to float or int if numpy - otherwise cannot jsonify endpoint return result
        if isinstance(record_details[col], numpy.float64):
            record_details[col] = float(record_details[col])

        if isinstance(record_details[col], numpy.int64):
            record_details[col] = int(record_details[col])

        # Convert from numpy bool to standard bool - otherwise cannot jsonify endpoint return result
        if isinstance(record_details[col], numpy.bool_):
            record_details[col] = bool(record_details[col])
    return record_details


def get_record_details(source_id):
    with db_session() as session:
        try:
            # Construct case when expression to generate isotype column based on isotype bool cols
            isotype_case_expression = _get_isotype_col_expression()

            # Build list of columns to use in query starting with airtable source columns
            fields_list = []
            for col in dashboard_source_cols:
                fields_list.append(getattr(DashboardSource, col))

            # Store info about supplementary tables to join to airtable source
            table_infos = db_model_config['supplementary_table_info']

            # Add columns from supplementary tables and add isotype col expression
            for sup_table in table_infos:
                fields_list.append(getattr(sup_table['main_table'], f"{sup_table['entity']}_name").label(sup_table['entity']))
            fields_list.append(getattr(Country, 'country_name').label('country'))

            query = session.query(*fields_list, isotype_case_expression)

            # Build query to join supplementary tables to airtable source
            for sup_table in table_infos:
                main_table = sup_table['main_table']
                bridge_table = sup_table['bridge_table']
                entity_id = f"{sup_table['entity']}_id"
                query = query.outerjoin(bridge_table, bridge_table.source_id == DashboardSource.source_id)\
                    .outerjoin(main_table, getattr(bridge_table, entity_id) == getattr(main_table, entity_id))

            # Join on country table
            query = query.outerjoin(Country, Country.country_id == DashboardSource.country_id)

            # Filter by input source id and convert results to dicts
            query = query.filter(DashboardSource.source_id == source_id)
            result = query.all()
            result = [x._asdict() for x in result]

            # If multiple records are returned, parse results to return one record
            if len(result) > 1:
                result = _get_parsed_record(result)
            else:
                result = result[0]

            # Convert dates to use isoformat
            if result['sampling_end_date'] is not None:
                result['sampling_end_date'] = result['sampling_end_date'].isoformat()
            if result['sampling_start_date'] is not None:
                result['sampling_start_date'] = result['sampling_start_date'].isoformat()

        except Exception as e:
            print(e)
    return result


def get_country_seroprev_summaries(records):
    # Turn records into df and remove list from country
    records_df = pd.DataFrame(records)

    # Get unique list of countries
    countries = records_df.country.dropna().unique()
    study_counts_list = []

    # For each country, create a payload with all the seroprev summary info
    for country in countries:
        country_seroprev_summary_dict = {}
        country_seroprev_summary_dict['country'] = country
        records_for_country = records_df[records_df['country'] == country]

        # Get country ISO3 code
        country_seroprev_summary_dict['country_iso3'] = records_for_country['country_iso3'].iloc[0]

        # Get total number of seroprev estimates in country
        country_seroprev_summary_dict['n_estimates'] = records_for_country.shape[0]

        # Get total number of tests administered in country
        country_seroprev_summary_dict['n_tests_administered'] = int(records_for_country.denominator_value.sum())

        # Summarize seroprev estimate info at each estimate grade level
        estimate_grades = ['National', 'Regional', 'Local', 'Sublocal', 'Hyperlocal']
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
                minimum = records_for_grade.serum_pos_prevalence.min()
                maximum = records_for_grade.serum_pos_prevalence.max()
                # Add min and max seroprev estimates
                estimate_grade_dict['min_estimate'] = minimum if not math.isnan(minimum) else None
                estimate_grade_dict['max_estimate'] = maximum if not math.isnan(maximum) else None
            grades_seroprev_summaries_dict[grade] = estimate_grade_dict
        country_seroprev_summary_dict['seroprevalence_estimate_summary'] = grades_seroprev_summaries_dict
        study_counts_list.append(country_seroprev_summary_dict)
    return study_counts_list


# Modify record coordinates
# to ensure that pins are not directly at the same location
def jitter_pins(records):
    locations_seen = set()
    for record in records:
        if record["pin_latitude"] and record["pin_longitude"]:
            loc = f"{record['pin_latitude']}_{record['pin_longitude']}"
            if loc in locations_seen:
                # For reference: 0.1 degrees is approx 11km at the equator
                lat_diff = uniform(-0.5, 0.5)
                lng_diff = uniform(-0.5, 0.5)
                record['pin_latitude'] += lat_diff
                record['pin_longitude'] += lng_diff
                locations_seen.add(f"{record['pin_latitude']}_{record['pin_longitude']}")
            else:
                locations_seen.add(loc)
    return records


def get_all_filter_options() -> Dict[str, Any]:
    with db_session() as session:
        options = get_filter_static_options()

        # Get countries
        query = session.query(distinct(getattr(Country, "country_name")))
        results = [q[0] for q in query if q[0] is not None]
        # sort countries in alpha order
        options["country"] = sorted(results)

        # Get genpop
        query = session.query(distinct(ResearchSource.genpop))
        results = [q[0] for q in query if q[0] is not None]
        options["genpop"] = sorted(results)

        # Get subgroup_var
        query = session.query(distinct(DashboardSource.subgroup_var))
        results = [q[0] for q in query if q[0] is not None]
        options["subgroup_var"] = sorted(results)

        # Get subgroup_cat
        query = session.query(distinct(ResearchSource.subgroup_cat))
        results = [q[0] for q in query if q[0] is not None]
        options["subgroup_cat"] = sorted(results)

        # Get state
        query = session.query(distinct(State.state_name))
        results = [q[0] for q in query if q[0] is not None]
        options["state"] = sorted(results)

        # Get city
        query = session.query(distinct(City.city_name))
        results = [q[0] for q in query if q[0] is not None]
        options["city"] = sorted(results)

        # Get antibody target
        query = session.query(distinct(AntibodyTarget.antibody_target_name))
        results = [q[0] for q in query if q[0] is not None]
        options["antibody_target"] = sorted(results)

        options["max_sampling_end_date"] = session.query(func.max(DashboardSource.sampling_end_date))[0][0].isoformat()
        options["min_sampling_end_date"] = session.query(func.min(DashboardSource.sampling_end_date))[0][0].isoformat()
        options["max_publication_end_date"] = session.query(func.max(DashboardSource.publication_date))[0][
            0].isoformat()
        options["min_publication_end_date"] = session.query(func.min(DashboardSource.publication_date))[0][
            0].isoformat()
        options["updated_at"] = session.query(func.max(DashboardSource.publication_date))[0][0].isoformat()

        # Get population group options
        results = session.query(PopulationGroupOptions.order, PopulationGroupOptions.name, PopulationGroupOptions.french_name)
        # result[0]: Order associated with filter option, records are sorted by this Order
        # result[1]: English translation of filter option
        # result[2]: French translation of filter option
        options["population_group"] = [[result[1], result[2]] for result in sorted(results, key=lambda result: result[0])]
        
        return options
