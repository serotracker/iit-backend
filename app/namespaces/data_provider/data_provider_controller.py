import logging.config

from flask_restx import Resource, Namespace
from flask import jsonify, make_response, request

from .data_provider_service import get_record_details, get_country_seroprev_summaries, jitter_pins, \
    get_all_filter_options
from .data_provider_schema import RecordDetailsSchema, RecordsSchema, PaginatedRecordsSchema, StudyCountSchema
from app.utils import validate_request_input_against_schema, get_filtered_records, get_paginated_records, \
    convert_start_end_dates, filter_columns
from ...utils.get_filtered_records import get_all_arbo_records

data_provider_ns = Namespace('data_provider', description='Endpoints for getting database records.')
logging.getLogger(__name__)


@data_provider_ns.route('/records', methods=['POST'])
class Records(Resource):
    @data_provider_ns.doc('An endpoint for getting all records from database with or without filters.')
    def post(self):
        # Convert input payload to json and throw error if it doesn't exist
        data = request.get_json()
        if not data:
            return {"message": "No input payload provided"}, 400

        # Log request info
        logging.info("Endpoint Type: {type}, Endpoint Path: {path}, Arguments: {args}, Payload: {payload}".format(
            type=request.environ['REQUEST_METHOD'],
            path=request.environ['PATH_INFO'],
            args=dict(request.args),
            payload=data))

        # All of these params can be empty, in which case, our utility functions will just return all records
        filters = data.get('filters')

        # Validate input payload
        payload, status_code = validate_request_input_against_schema(data, RecordsSchema())
        if status_code != 200:
            # If there was an error with the input payload, return the error and 422 response
            return make_response(payload, status_code)

        columns_requested = data.get('columns')
        research_fields = data.get('research_fields')
        estimates_subgroup = data.get('estimates_subgroup', 'all_estimates')
        prioritize_estimates_mode = data.get('prioritize_estimates_mode', 'dashboard')
        include_disputed_regions = data.get('include_disputed_regions', False)
        include_subgeography_estimates = data.get('include_subgeography_estimates', False)
        unity_aligned_only = data.get('unity_aligned_only', False)
        include_records_without_latlngs = data.get('include_records_without_latlngs', False)
        calculate_country_seroprev_summaries = data.get('calculate_country_seroprev_summaries', True)

        sampling_start_date, sampling_end_date = convert_start_end_dates(data, use_sampling_date=True)
        publication_start_date, publication_end_date = convert_start_end_dates(data, use_sampling_date=False)
        include_in_srma = data.get('include_in_srma', False)

        # Making a copy of columns_requested here because we will need its original value later on
        columns = columns_requested
        # If we intend to calculate country summaries we will need certain columns
        if calculate_country_seroprev_summaries and columns:
            COUNTRY_SEROPREV_SUMMARY_COLS = ['country', 'country_iso3', 'denominator_value', 'serum_pos_prevalence',
                                             'estimate_grade']
            columns = list(set(COUNTRY_SEROPREV_SUMMARY_COLS).union(set(columns)))

        records = get_filtered_records(research_fields,
                                       filters,
                                       columns,
                                       sampling_start_date=sampling_start_date,
                                       sampling_end_date=sampling_end_date,
                                       publication_start_date=publication_start_date,
                                       publication_end_date=publication_end_date,
                                       estimates_subgroup=estimates_subgroup,
                                       prioritize_estimates_mode=prioritize_estimates_mode,
                                       include_in_srma=include_in_srma,
                                       include_disputed_regions=include_disputed_regions,
                                       include_subgeography_estimates=include_subgeography_estimates,
                                       unity_aligned_only=unity_aligned_only,
                                       include_records_without_latlngs=include_records_without_latlngs)

        print(records)

        if not columns or ("pin_latitude" in columns and "pin_longitude" in columns):
            records = jitter_pins(records)

        result = {"records": records}

        if calculate_country_seroprev_summaries:
            # Compute seroprevalence summaries per country per estimate grade level
            country_seroprev_summaries = get_country_seroprev_summaries(records)
            result["country_seroprev_summary"] = country_seroprev_summaries
            # Ensure that we only return the requested columns to streamline data sent over HTTP
            if columns_requested:
                result["records"] = filter_columns(result["records"], columns_requested)
        return jsonify(result)


@data_provider_ns.route('/records/arbo', methods=['GET'])
class ArboRecords(Resource):
    @data_provider_ns.doc('An endpoint for getting all arbotracker records from database with or without filters.')
    def get(self):

        records = get_all_arbo_records()

        result = {"records": records}

        print(result)

        return jsonify(result)


# TODO: Deprecate
@data_provider_ns.route('/records/paginated', methods=['POST'])
class PaginatedRecords(Resource):
    @data_provider_ns.doc('An endpoint for getting all paginated records from database with or without filters.')
    def post(self):
        # Convert input payload to json and throw error if it doesn't exist
        data = request.get_json()
        if not data:
            return {"message": "No input payload provided"}, 400

        # Log request info
        logging.info("Endpoint Type: {type}, Endpoint Path: {path}, Arguments: {args}, Payload: {payload}".format(
            type=request.environ['REQUEST_METHOD'],
            path=request.environ['PATH_INFO'],
            args=dict(request.args),
            payload=data))

        # All of these params can be empty, in which case, our utility functions will just return all records
        filters = data.get('filters')

        # Validate input payload
        payload, status_code = validate_request_input_against_schema(data, PaginatedRecordsSchema())
        if status_code != 200:
            # If there was an error with the input payload, return the error and 422 response
            return make_response(payload, status_code)

        sorting_key = data.get('sorting_key', None)
        min_page_index = data.get('min_page_index')
        max_page_index = data.get('max_page_index')
        per_page = data.get('per_page', None)
        reverse = data.get('reverse', None)
        columns = data.get('columns')
        research_fields = data.get('research_fields')
        estimates_subgroup = data.get('estimates_subgroup', 'all_estimates')
        prioritize_estimates_mode = data.get('prioritize_estimates_mode', 'dashboard')
        sampling_start_date, sampling_end_date = convert_start_end_dates(data, use_sampling_date=True)
        include_in_srma = data.get('include_in_srma', False)

        result = get_filtered_records(research_fields, filters, columns,
                                      sampling_start_date=sampling_start_date,
                                      sampling_end_date=sampling_end_date,
                                      estimates_subgroup=estimates_subgroup,
                                      prioritize_estimates_mode=prioritize_estimates_mode,
                                      include_in_srma=include_in_srma)
        if not columns or ("pin_latitude" in columns and "pin_longitude" in columns):
            result = jitter_pins(result)

        kwargs = {
            "records": result,
            "min_page_index": min_page_index,
            "max_page_index": max_page_index,
            "per_page": per_page,
            "reverse": reverse,
            "sorting_key": sorting_key
        }

        kwargs_not_none = {k: v for k, v in kwargs.items() if v is not None}

        # Only paginate if pagination params min_page_index, max_page_index and per_page are specified (sorting_key="sampling_end_date", reverse=true, per_page=5 by default)
        result = get_paginated_records(**kwargs_not_none)
        return jsonify(result)


@data_provider_ns.route('/record_details/<string:source_id>', methods=['GET'])
@data_provider_ns.param('source_id', 'The primary key of the Airtable Source table that identifies a record.')
class RecordDetails(Resource):
    @data_provider_ns.doc('An endpoint for getting the details of a record based on source id.')
    def get(self, source_id):
        # Log request info
        logging.info("Endpoint Type: {type}, Endpoint Path: {path}, Arguments: {args}".format(
            type=request.environ['REQUEST_METHOD'],
            path=request.environ['PATH_INFO'],
            args=dict(request.args)))

        # Validate input
        payload, status_code = validate_request_input_against_schema({'source_id': source_id}, RecordDetailsSchema())
        if status_code != 200:
            # If there was an error with the input payload, return the error and 422 response
            return make_response(payload, status_code)

        # Get record details based on the source_id of the record
        record_details = get_record_details(source_id)
        return jsonify(record_details)


# TODO: Deprecate
@data_provider_ns.route('/country_seroprev_summary', methods=['GET', 'POST'])
class GeogStudyCount(Resource):
    @data_provider_ns.doc('An endpoint for summarizing the seroprevalence data of a country.')
    def get(self):
        # Log request info
        logging.info("Endpoint Type: {type}, Endpoint Path: {path}, Arguments: {args}".format(
            type=request.environ['REQUEST_METHOD'],
            path=request.environ['PATH_INFO'],
            args=dict(request.args)))

        # Query all the records with no filters but only grab certain columns
        columns = ['country', 'country_iso3', 'denominator_value', 'serum_pos_prevalence', 'estimate_grade']
        records = get_filtered_records(filters=None, columns=columns, sampling_start_date=None, sampling_end_date=None)

        # Compute seroprevalence summaries per country per estimate grade level
        country_seroprev_summaries = get_country_seroprev_summaries(records)
        return jsonify(country_seroprev_summaries)

    def post(self):
        # Ensure payload is present
        json_input = request.get_json()
        if not json_input:
            return make_response({"message": "No input payload provided"}, 400)

        # Log request info
        logging.info("Endpoint Type: {type}, Endpoint Path: {path}, Arguments: {args}, Payload: {payload}".format(
            type=request.environ['REQUEST_METHOD'],
            path=request.environ['PATH_INFO'],
            args=dict(request.args),
            payload=json_input))

        # Validate input payload
        payload, status_code = validate_request_input_against_schema(json_input, StudyCountSchema())
        if status_code != 200:
            # If there was an error with the input payload, return the error and 422 response
            return make_response(payload, status_code)

        # Query all the records with the desired filters. Pull only country, denom, and seroprev cols
        filters = json_input.get('filters')
        sampling_start_date, sampling_end_date = convert_start_end_dates(json_input, use_sampling_date=True)
        unity_aligned_only = json_input.get('unity_aligned_only', False)
        columns = ['country', 'country_iso3', 'denominator_value', 'serum_pos_prevalence', 'estimate_grade']
        records = get_filtered_records(filters=filters,
                                       columns=columns,
                                       sampling_start_date=sampling_start_date,
                                       sampling_end_date=sampling_end_date,
                                       unity_aligned_only=unity_aligned_only)

        # Check if no records are returned
        if not records:
            return jsonify(records)

        # Compute seroprevalence summaries per country per estimate grade level
        country_seroprev_summaries = get_country_seroprev_summaries(records)
        return jsonify(country_seroprev_summaries)


@data_provider_ns.route('/filter_options', methods=['GET'])
class Records(Resource):
    @data_provider_ns.doc('An endpoint for getting all filter options from the database.')
    def get(self):
        # Log request info
        logging.info("Endpoint Type: {type}, Endpoint Path: {path}, Arguments: {args}".format(
            type=request.environ['REQUEST_METHOD'],
            path=request.environ['PATH_INFO'],
            args=dict(request.args)))

        result = get_all_filter_options()
        return jsonify(result)
