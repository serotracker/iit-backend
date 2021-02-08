import logging

from flask_restplus import Resource, Namespace
from flask import make_response, request

from app.utils import validate_request_input_against_schema, get_filtered_records, convert_start_end_dates
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

        # Log request info
        logging.info("Endpoint Type: {type}, Endpoint Path: {path}, Arguments: {args}, Payload: {payload}".format(
            type=request.environ['REQUEST_METHOD'],
            path=request.environ['PATH_INFO'],
            args=dict(request.args),
            payload=json_input))

        # Validate input payload
        payload, status_code = validate_request_input_against_schema(json_input, MetaSchema())
        if status_code != 200:
            # If there was an error with the input payload, return the error and 422 response
            return make_response(payload, status_code)

        # If payload was successfully validated, extract fields
        agg_var = json_input.get('aggregation_variable', None)

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

        # Query all the records with the desired filters. Pull only country, denom, and seroprev cols
        filters = json_input.get('filters', None)
        start_date, end_date = convert_start_end_dates(json_input)
        columns = ['country', 'denominator_value', 'serum_pos_prevalence']
        columns.append(agg_var)
        records = get_filtered_records(filters=filters, columns=columns, start_date=start_date, end_date=end_date)
        if not records:
            logging.warning('No records with specified filters found.')
            return {}

        meta_analysis_results = get_meta_analysis_records(records, agg_var, meta_transformation, meta_technique)
        return meta_analysis_results
