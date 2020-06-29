import logging

from flask_restplus import Resource, Namespace
from flask import jsonify, make_response, request, current_app as app

from app.utils import validate_request_input_against_schema
from .meta_analysis_schema import MetaSchema
from .meta_analysis_service import get_meta_analysis_records

logger = logging.getLogger(__name__)

meta_analysis_ns =\
    Namespace('meta_analysis', description='An endpoint for performing meta analysis on a set of records.')


@meta_analysis_ns.route('/records', methods=['POST'])
class MetaAnalysis(Resource):
    @meta_analysis_ns.doc('An endpoint for performing meta analysis on a set of records'
                          'based on an aggregation variable and a meta analysis technique.')
    def post(self):
        # Ensure payload is present
        json_input = request.get_json()
        if not json_input:
            return make_response({"message": "No input payload provided"}, 400)

        # Validate input payload
        payload = validate_request_input_against_schema(json_input, MetaSchema())
        if not isinstance(payload, dict):
            # If there was an error with the input payload, return the error and 422 response
            return payload

        # If payload was successfully validated, extract fields
        records = json_input['records']
        agg_var = json_input['aggregation_variable']

        # Extract meta transformation variable if present and validate it, else set to default
        try:
            meta_transformation = json_input['meta_analysis_transformation']
            if meta_transformation not in ['unstransformed', 'logit', 'arcsin',
                                           'double_arcsin_approx', 'double_arcsin_precise']:
                logging.warning("'{}' is not a valid meta analysis transformation.".format(meta_transformation))
                meta_transformation = 'double_arcsin_precise'
        except KeyError:
            meta_transformation = 'double_arcsin_precise'

        # Extract meta technique variable if present and validate it, else set to default
        try:
            meta_technique = json_input['meta_analysis_technique']
            if meta_technique not in ['fixed', 'random', 'median']:
                logging.warning("'{}' is not a valid meta analysis technique.".format(meta_technique))
                meta_technique = 'fixed'
        except KeyError:
            meta_technique = 'fixed'

        meta_analysis_results = get_meta_analysis_records(records, agg_var, meta_transformation, meta_technique)
        return meta_analysis_results
