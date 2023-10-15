from sqlalchemy import distinct, func
from sqlalchemy.orm import Session

from Pathogens.Arbo.app.sqlalchemy.sql_alchemy_base import db_engine
from app.database_etl.postgres_tables_handler.postgres_utils import get_filter_static_options
from app.namespaces.data_provider.data_provider_service import _get_parsed_record
from app.serotracker_sqlalchemy.models import AntibodyTarget, PopulationGroupOptions, ResearchSource
from app.utils.get_filtered_records import _get_isotype_col_expression
from app.serotracker_sqlalchemy import DashboardSource, Country, db_model_config, dashboard_source_cols, State, City


def get_all_sarscov2_records():
    with Session(db_engine) as session:
            # session.query(Estimate, func.array_agg(Antibody.antibody).label("antibodies")).\
            # join(AntibodyToEstimate, Estimate.id == AntibodyToEstimate.estimate_id).\
            # join(Antibody, Antibody.id == AntibodyToEstimate.antibody_id).\
            # group_by(Estimate.id).all()

        try:
            # Selecting only the required columns from the DashboardSource table
            # TODO: Isotype reported and antibody target need to be added in

            records = session.query(
                DashboardSource.study_name,
                DashboardSource.estimate_grade,
                DashboardSource.source_type,
                DashboardSource.overall_risk_of_bias,
                DashboardSource.population_group,
                DashboardSource.sex,
                DashboardSource.age,
                DashboardSource.test_type,
                DashboardSource.pin_latitude,
                DashboardSource.pin_longitude,
            ).all()

            # Convert each record into a dictionary of column name and value pairs
            records = [dict(zip(record.keys(), record)) for record in records]

            result_list = []

            result_list.extend(records)

            for record in result_list[0:5]:
                print(f'[DEBUG] estimate record: {record}')
                print("--------------------")

        except Exception as e:
            print("ERROR", e)
    
    return result_list


def get_all_sarscov2_filter_options():
    
    with Session(db_engine) as session:

        options = get_filter_static_options()

        # # Get countries
        # query = session.query(distinct(getattr(Country, "country_name")))
        # results = [q[0] for q in query if q[0] is not None]
        # # sort countries in alpha order
        # options["country"] = sorted(results)

        # # Get genpop
        # query = session.query(distinct(ResearchSource.genpop))
        # results = [q[0] for q in query if q[0] is not None]
        # options["genpop"] = sorted(results)

        # # Get subgroup_var
        # query = session.query(distinct(DashboardSource.subgroup_var))
        # results = [q[0] for q in query if q[0] is not None]
        # options["subgroup_var"] = sorted(results)

        # # Get subgroup_cat
        # query = session.query(distinct(ResearchSource.subgroup_cat))
        # results = [q[0] for q in query if q[0] is not None]
        # options["subgroup_cat"] = sorted(results)

        # # Get state
        # query = session.query(distinct(State.state_name))
        # results = [q[0] for q in query if q[0] is not None]
        # options["state"] = sorted(results)

        # # Get city
        # query = session.query(distinct(City.city_name))
        # results = [q[0] for q in query if q[0] is not None]
        # options["city"] = sorted(results)

        # Only surface Spike and Nucleocapsid anitbody target options because only options that are relevant for
        # interpreting seroprev data in the context of vaccines
        query = session.query(distinct(AntibodyTarget.antibody_target_name))
        results = [q[0] for q in query if q[0] is not None and q[0] in ['Spike', 'Nucleocapsid (N-protein)']]
        options["antibody_target"] = sorted(results)

        # options["max_sampling_end_date"] = session.query(func.max(DashboardSource.sampling_end_date))[0][0].isoformat()
        # options["min_sampling_end_date"] = session.query(func.min(DashboardSource.sampling_end_date))[0][0].isoformat()
        # options["max_publication_end_date"] = session.query(func.max(DashboardSource.publication_date))[0][
        #     0].isoformat()
        # options["min_publication_end_date"] = session.query(func.min(DashboardSource.publication_date))[0][
        #     0].isoformat()
        # options["last_updated"] = session.query(func.max(DashboardSource.created_at))[0][0].isoformat()
        # options["most_recent_publication_date"] = \
        #     session.query(func.max(DashboardSource.publication_date))[0][0].isoformat()


        # Get population group options
        results = session.query(PopulationGroupOptions.order, PopulationGroupOptions.name, PopulationGroupOptions.french_name, PopulationGroupOptions.german_name)
        # result[0]: Order associated with filter option, records are sorted by this Order
        # result[1]: English translation of filter option
        # result[2]: French translation of filter option
        options["population_group"] = [{"english": result[1], "french": result[2], "german": result[3]} for result in sorted(results, key=lambda result: result[0])]
        
        return options