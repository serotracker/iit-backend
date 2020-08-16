import json
from datetime import datetime

from flask_restplus import Resource, Namespace
from flask import jsonify, make_response, request

from .data_provider_service import get_record_details, get_country_seroprev_summaries
from .data_provider_schema import RecordDetailsSchema, RecordsSchema, StudyCountSchema
from app.utils import validate_request_input_against_schema, get_filtered_records, get_paginated_records

data_provider_ns = Namespace('data_provider', description='Endpoints for getting database records.')


@data_provider_ns.route('/records', methods=['POST'])
class Records(Resource):
    @data_provider_ns.doc('An endpoint for getting all records from database')
    def post(self):
        data = request.get_json()

        # All of these params can be empty, in which case, our utility functions will just return all records
        filters = data.get('filters')
        if filters:
            filters = json.loads(filters)
            data["filters"] = filters

        # Validate input payload
        payload, status_code = validate_request_input_against_schema(data, RecordsSchema())
        if status_code != 200:
            # If there was an error with the input payload, return the error and 422 response
            return make_response(payload, status_code)

        sorting_key = data.get('sorting_key')
        page_index = data.get('page_index')
        per_page = data.get('per_page')
        reverse = data.get('reverse')

        start_date = data.get('start_date')
        if start_date:
            start_date = datetime.utcfromtimestamp(start_date)
        end_date = data.get('end_date')
        if end_date:
            end_date = datetime.utcfromtimestamp(end_date)

        filtered_records = get_filtered_records(filters, start_date=start_date, end_date=end_date)
        result = get_paginated_records(filtered_records, sorting_key, page_index, per_page, reverse)

        return jsonify(result)


@data_provider_ns.route('/record_details/<string:source_id>', methods=['GET'])
@data_provider_ns.param('source_id', 'The primary key of the Airtable Source table that identifies a record.')
class RecordDetails(Resource):
    @data_provider_ns.doc('An endpoint for getting the details of a record based on source id.')
    def get(self, source_id):
        # Validate input
        payload, status_code = validate_request_input_against_schema({'source_id': source_id}, RecordDetailsSchema())
        if status_code != 200:
            # If there was an error with the input payload, return the error and 422 response
            return make_response(payload, status_code)

        # Get record details based on the source_id of the record
        record_details = get_record_details(source_id)
        return jsonify(record_details)


@data_provider_ns.route('/country_seroprev_summary', methods=['POST'])
class GeogStudyCount(Resource):
    @data_provider_ns.doc('An endpoint for summarizing the seroprevalence data of a country.')
    def post(self):
        # Ensure payload is present
        json_input = request.get_json()
        if not json_input:
            return make_response({"message": "No input payload provided"}, 400)

        # Validate input payload
        payload, status_code = validate_request_input_against_schema(json_input, StudyCountSchema())
        if status_code != 200:
            # If there was an error with the input payload, return the error and 422 response
            return make_response(payload, status_code)

        country_seroprev_summaries = get_country_seroprev_summaries(json_input['records'])
        return jsonify(country_seroprev_summaries)
