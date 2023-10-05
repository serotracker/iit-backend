import pandas as pd
from sqlalchemy import func
from sqlalchemy.orm import Session

from Pathogens.Arbo.API.Services.records_service import get_all_arbo_records
from Pathogens.Arbo.app.sqlalchemy import db_engine
from Pathogens.Arbo.app.sqlalchemy.sql_alchemy_base import Estimate, Antibody, AntibodyToEstimate


# If doing the same on the front end, then consider using nodejs-polars
# For now will send an API call with filters to the backend and return the data for the visualizations

# Will have to test which is better, data handling backend or data handling frontend



def get_arbo_visualizations():

    # all_records = get_all_arbo_records()

    # Generate sql queries that get this data for me and then format it
    # Count of studies by assay type strat by pathogen - Bar - Done

    # {data: [{
    #   x-axis-tick: x-axis-value
    #   strat-variable-1: y-axis-value
    #   ...
    #   strat-variable-n: y-axis-value
    #  }...],
    #  keys: [strat-variables],
    #  indexBy: x-axis-label,
    #  x-axis-label: x-axis-label,
    #  y-axis-label: y-axis-label
    # }
    with Session(db_engine) as session:
        CountAssayPathogens = session.query(Estimate.assay, Estimate.pathogen, func.count().label('counts')) \
            .filter(Estimate.assay.isnot(None))\
            .group_by(Estimate.assay, Estimate.pathogen)\
            .all()

        df = pd.DataFrame(CountAssayPathogens, columns=['assay', 'pathogen', 'counts'])

        pivot_df = df.pivot(index='pathogen', columns='assay', values='counts').fillna(0)

        # Convert the pivot table to a list of dictionaries
        pathogen_data = []
        for pathogen, counts in pivot_df.iterrows():
            # Check if pathogen is NaN and skip it
            if not pd.isna(pathogen):
                record = {"pathogen": pathogen}
                record.update(counts.to_dict())
                pathogen_data.append(record)

        # Create the result dictionary with swapped columns
        pathogenResult = {
            "chartType": "bar",
            "data": pathogen_data,
            "keys": df['assay'].unique().tolist(),
            "indexBy": "pathogen",
            "xAxisLabel": "Pathogen Type",
            "yAxisLabel": "Count of Studies"
        }

    # cumulative number of studies over time strat by pathogen - area
    # cumulative number of studies over time strat by sample frame - area

    # More Complex as need to process data using countries and lists of region divisions - both use same sql query to begin with
    # Count of studies in WHO region strat by pathogen - Bar
    # Count of arbo studies per region and subregion - BAR

    # might need to get all data and then do the work. Or the query gets more complex as we can have IgG and IgM
    # Count of studies by antibody type strat by pathogen - Bar

    # Clarify with Reza
    # Seroprevalence estimates by pathogen - boxplot - What is the math here?

    # Missing Data
    # Count of studies by design strat by pathogen - Bar
    # Count of studies by sampling method strat by pathogen - Bar

    return [pathogenResult]