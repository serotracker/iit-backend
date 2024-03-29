import json

from Pathogens.Arbo.app.sqlalchemy.sql_alchemy_base import Estimate
from app.serotracker_sqlalchemy import db_session, DashboardSource, ResearchSource, \
    db_model_config, Country, dashboard_source_cols, research_source_cols, ArboRecords
from sqlalchemy.dialects.postgresql import array
from sqlalchemy import func, cast, case, and_, String, ARRAY
import pandas as pd
import numpy as np
from app.utils.estimate_prioritization import get_prioritized_estimates, get_prioritized_estimates_without_pooling

from sqlalchemy.sql.visitors import VisitableType as SQLalchemyType
from sqlalchemy.orm.attributes import InstrumentedAttribute as SQLalchemyExpression
from sqlalchemy.sql.elements import Label as SQLAlchemyLabelExpression
from typing import List, Dict, Any


def _get_isotype_col_expression(label: str = "isotypes"):
    expression = case(
        [
            (and_(DashboardSource.isotype_igg == 'true',
                  DashboardSource.isotype_igm == 'true',
                  DashboardSource.isotype_iga == 'true'), array(["IgG", "IgM", "IgA"])),
            (and_(DashboardSource.isotype_igg == 'true',
                  DashboardSource.isotype_igm == 'false',
                  DashboardSource.isotype_iga == 'true'), array(["IgG", "IgA"])),
            (and_(DashboardSource.isotype_igg == 'true',
                  DashboardSource.isotype_igm == 'true',
                  DashboardSource.isotype_iga == 'false'), array(["IgG", "IgM"])),
            (and_(DashboardSource.isotype_igg == 'false',
                  DashboardSource.isotype_igm == 'true',
                  DashboardSource.isotype_iga == 'true'), array(["IgM", "IgA"])),
            (and_(DashboardSource.isotype_igg == 'true',
                  DashboardSource.isotype_igm == 'false',
                  DashboardSource.isotype_iga == 'false'), array(["IgG"])),
            (and_(DashboardSource.isotype_igg == 'false',
                  DashboardSource.isotype_igm == 'false',
                  DashboardSource.isotype_iga == 'true'), array(["IgA"])),
            (and_(DashboardSource.isotype_igg == 'false',
                  DashboardSource.isotype_igm == 'true',
                  DashboardSource.isotype_iga == 'false'), array(["IgM"]))
        ],
        else_=cast(array([]), ARRAY(String))).label(label)
    return expression


# Query to aggregate multiple multi select options into a single array
# Note: case statement is used so that we show [] instead of [None]
# agg_field_exp --> sqlalchemy expression representing the field you'd like to aggregate (e.g. State.Longitude)
def _apply_agg_query(agg_field_exp: SQLalchemyExpression, label: str,
                     type: SQLalchemyType = String) -> SQLAlchemyLabelExpression:
    return case([(func.array_agg(agg_field_exp).filter(agg_field_exp.isnot(None)).isnot(None),
                  cast(func.array_agg(func.distinct(agg_field_exp)).filter(agg_field_exp.isnot(None)), ARRAY(type)))],
                else_=cast(array([]), ARRAY(type))).label(label)



def get_all_records(research_fields=False, include_disputed_regions=False,
                    unity_aligned_only=False, include_records_without_latlngs=False):
    with db_session() as session:
        # Get all records for now, join on all tables
        table_infos = db_model_config['supplementary_table_info']

        # Add columns from dashboard source to select statement
        fields_list = [DashboardSource.source_id]
        for field_string in dashboard_source_cols:
            fields_list.append(getattr(DashboardSource, field_string))

        # If research fields is True, add columns from research source to select statement
        if research_fields:
            for col in research_source_cols:
                fields_list.append(getattr(ResearchSource, col))

        # Alias for country name and iso3 code
        fields_list.append(Country.country_name.label("country"))
        fields_list.append(Country.country_iso3.label("country_iso3"))
        fields_list.append(Country.income_class.label("income_class"))
        fields_list.append(Country.hrp_class.label("hrp_class"))

        # Will need to group by every field that isn't array aggregated
        # using copy here since python assigns list variables by ref instead of by value
        groupby_fields = fields_list.copy()

        for table_info in table_infos:
            # The label method returns an alias for the column being queried
            # Use case: We want to get fields from the bridge table without the _name suffix
            fields_list.append(_apply_agg_query(getattr(table_info["main_table"], f"{table_info['entity']}_name"),
                                                table_info['entity']))

        query = session.query(*fields_list, _get_isotype_col_expression(label="isotypes_reported"))

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

        # Filter out estimates in disputed areas if necessary
        if not include_disputed_regions:
            query = query.filter(DashboardSource.in_disputed_area == False)

        # Filter out non unity aligned studies if necessary
        if unity_aligned_only:
            query = query.filter(DashboardSource.is_unity_aligned == True)

        # Filter out records without latlngs
        if not include_records_without_latlngs:
            query = query.filter(DashboardSource.pin_latitude.isnot(None)). \
                filter(DashboardSource.pin_longitude.isnot(None))

        # Need to apply group by so that array_agg works as expected
        query = query.group_by(*groupby_fields)

        query = query.all()
        # Convert from sqlalchemy object to dict
        query_dict = [q._asdict() for q in query]

        return query_dict


def get_filtered_records(research_fields=False, filters=None, columns=None, include_disputed_regions=False,
                         sampling_start_date=None, sampling_end_date=None, include_subgeography_estimates=False,
                         publication_start_date=None, publication_end_date=None, estimates_subgroup='all',
                         prioritize_estimates_mode='dashboard', include_in_srma=False, unity_aligned_only=False,
                         include_records_without_latlngs=False):
    # Get all records from the database as a list of records represented by dicts
    query_dicts = get_all_records(research_fields, include_disputed_regions, unity_aligned_only,
                                  include_records_without_latlngs)

    if query_dicts is None or len(query_dicts) == 0:
        return []

    # If estimates_subgroup is 'estimate_prioritization', perform estimate prioritization
    if estimates_subgroup == 'prioritize_estimates':
        result_df = pd.DataFrame(query_dicts)
        if include_subgeography_estimates:
            prioritized_records = get_prioritized_estimates_without_pooling(result_df,
                                                                            subgroup_var="Geographical area",
                                                                            mode=prioritize_estimates_mode)
        else:
            prioritized_records = get_prioritized_estimates(result_df, mode=prioritize_estimates_mode)
        # If records exist, clean dataframe
        if not prioritized_records.empty:
            # Convert from True/None to True/False
            for col in prioritized_records.columns:
                # Note purpose of this line is to check if the col in question is a boolean col
                # Can't simply check the dtype because cols with True/None instead of
                # True/False have dtype="object" instead of "bool"
                if True in prioritized_records[col].values:
                    prioritized_records[col] = prioritized_records[col].fillna(False)
            prioritized_records = prioritized_records.fillna(np.nan).replace({np.nan: None})
        query_dicts = prioritized_records.to_dict('records')

    # If estimates_subgroup is 'primary_estimates', just return the primary estimate for each study
    # Otherwise, estimates_subgroup = 'all' so just return all estimates
    elif estimates_subgroup == 'primary_estimates':
        result_df = pd.DataFrame(query_dicts)
        primary_estimates_df = result_df.loc[result_df['dashboard_primary_estimate'] == True]
        primary_estimates_df = primary_estimates_df.fillna(np.nan).replace({np.nan: None})
        query_dicts = primary_estimates_df.to_dict('records')

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
        isoformat_fields = \
            ['sampling_end_date', 'sampling_start_date', 'publication_date', 'date_created', 'last_modified_time']
        for field in isoformat_fields:
            if record.get(field, None) is not None:
                record[field] = record[field].isoformat()

    # Need to check if 'research_fields' is applied
    # because the include_in_srma field is in the ResearchSource table
    if include_in_srma and research_fields:
        result = [estimate for estimate in result if estimate['include_in_srma']]

    # Finally, if columns have been supplied, only return those columns
    if columns is not None and len(columns) > 0:
        filter_columns(result, columns)

    return result


def filter_columns(records, cols_to_include):
    def grab_cols(result, columns):
        ret = {}
        for col in columns:
            ret[col] = result.get(col)
        return ret

    return [grab_cols(i, cols_to_include) for i in records]


def get_paginated_records(records: List[Dict[str, Any]], min_page_index: int, max_page_index: int, per_page: int = 5,
                          reverse: bool = False, sorting_key: str = "sampling_end_date") -> Dict[
    int, List[Dict[str, Any]]]:
    '''Gets and returns a dictionary of pages of records
    :param records: list of unpaginated records
    :param min_page_index: minimum page index
    :param max_page_index: maximum page index
    :param per_page: number of records per page
    :param reverse: whether to sort list of unpaginated records in reverse order or not
    :param sorting_key: key by which list of unpaginated records are sorted
    :returns a dictionary of lists of records (len(list) == per_page)
    '''
    # Order the records first
    sorted_records = sorted(records, key=lambda x: (x[sorting_key] is None, x[sorting_key]), reverse=reverse)
    # Input is non-zero indexing, but we map to zero indexing (e.g. input 1-3 maps to 0-2)
    # but we still return non-zero indexing
    min_page_index -= 1
    max_page_index -= 1

    # Create dictionary of pages of records
    return {i + 1: sorted_records[i * per_page:i * per_page + per_page]
    if i * per_page + per_page < len(sorted_records)
    else sorted_records[i * per_page:]
            for i in range(min_page_index, max_page_index + 1)}
