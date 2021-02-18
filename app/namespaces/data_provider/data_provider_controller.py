import logging.config

from flask_restplus import Resource, Namespace
from flask import jsonify, make_response, request

from .data_provider_service import get_record_details, get_country_seroprev_summaries, jitter_pins
from .data_provider_schema import RecordDetailsSchema, RecordsSchema, StudyCountSchema
from app.utils import validate_request_input_against_schema, get_filtered_records,\
    get_paginated_records, convert_start_end_dates
from app.database_etl.postgres_tables_handler import get_all_filter_options

data_provider_ns = Namespace('data_provider', description='Endpoints for getting database records.')
logging.getLogger(__name__)


@data_provider_ns.route('/records', methods=['GET', 'POST'])
class Records(Resource):
    @data_provider_ns.doc('An endpoint for getting all records from database with or without filters.')
    def get(self):
        # Parse pagination request args if they are present
        sorting_key = request.args.get('sorting_key', None, type=str)
        min_page_index = request.args.get('min_page_index', None, type=int)
        max_page_index = request.args.get('max_page_index', None, type=int)
        per_page = request.args.get('per_page', None, type=int)

        # Type must be string not bool, because bool evaluates to true for any non None value including False and True
        research_fields = False if str.lower(request.args.get('research_fields', 'false', type=str)) == 'false' else True
        prioritize_estimates = True if str.lower(request.args.get('prioritize_estimates', 'true', type=str)) == 'true' else False
        reverse = False if str.lower(request.args.get('reverse', 'false', type=str)) == 'false' else True

        # Log request info
        logging.info("Endpoint Type: {type}, Endpoint Path: {path}, Arguments: {args}".format(
            type=request.environ['REQUEST_METHOD'],
            path=request.environ['PATH_INFO'],
            args=dict(request.args)))

        result = get_filtered_records(research_fields, filters=None, columns=None, start_date=None, end_date=None,
                                      prioritize_estimates=prioritize_estimates)
        result = jitter_pins(result)

        # Only paginate if all the pagination parameters have been specified
        if min_page_index is not None and max_page_index is not None and per_page is not None and sorting_key is not None and reverse is not None:
            result = get_paginated_records(result, sorting_key, min_page_index, max_page_index, per_page, reverse)
        return jsonify(result)

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

        sorting_key = data.get('sorting_key')
        min_page_index = data.get('min_page_index')
        max_page_index = data.get('max_page_index')
        per_page = data.get('per_page')
        reverse = data.get('reverse')
        columns = data.get('columns')
        research_fields = data.get('research_fields')
        prioritize_estimates = data.get('prioritize_estimates', True)
        start_date, end_date = convert_start_end_dates(data)

        result = get_filtered_records(research_fields, filters, columns, start_date=start_date, end_date=end_date,
                                      prioritize_estimates=prioritize_estimates)
        if not columns or ("pin_latitude" in columns and "pin_longitude" in columns):
            result = jitter_pins(result)

        # Only paginate if all the pagination parameters have been specified
        if min_page_index is not None and max_page_index is not None and per_page is not None and sorting_key is not None and reverse is not None:
            result = get_paginated_records(result, sorting_key, min_page_index, max_page_index, per_page, reverse)
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
        records = get_filtered_records(filters=None, columns=columns, start_date=None, end_date=None)

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
        start_date, end_date = convert_start_end_dates(json_input)
        columns = ['country', 'country_iso3', 'denominator_value', 'serum_pos_prevalence', 'estimate_grade']
        records = get_filtered_records(filters=filters, columns=columns, start_date=start_date, end_date=end_date)

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
