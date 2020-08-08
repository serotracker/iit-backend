from flask_restplus import Resource, Namespace
from flask import jsonify, make_response

from .estimates_provider_service import get_record_details
from .estimates_provider_schema import RecordDetailsSchema
from app.utils import validate_request_input_against_schema

estimates_provider_ns = Namespace('estimates_provider', description='An endpoint for scraping airtable data.')


@estimates_provider_ns.route('/record_details/<string:source_id>', methods=['GET'])
@estimates_provider_ns.param('source_id', 'The primary key of the Airtable Source table that identifies a record.')
class RecordDetails(Resource):
    @estimates_provider_ns.doc('An endpoint for getting the details of a record based on source id.')
    def get(self, source_id):
        # Validate input
        payload, status_code = validate_request_input_against_schema({'source_id': source_id}, RecordDetailsSchema())
        if status_code != 200:
            # If there was an error with the input payload, return the error and 422 response
            return make_response(payload, status_code)

        # Get record details based on the source_id of the record
        record_details = get_record_details(source_id)
        return jsonify(record_details)
