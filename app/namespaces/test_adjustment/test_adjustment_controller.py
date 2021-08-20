import logging.config
import multiprocessing

from flask_restplus import Resource, Namespace
from flask import jsonify, make_response, request

from app.utils import validate_request_input_against_schema
from .test_adjustment_schema import TestAdjustmentSchema
from .test_adjustment_service import TestAdjHandler


test_adjustment_ns = Namespace('test_adjustment', description='Endpoints for updating airtable records via scripting.')
logging.getLogger(__name__)


@test_adjustment_ns.route('/get_adjusted', methods=['POST'])
class Records(Resource):
    @test_adjustment_ns.doc('An endpoint for getting all records from database with or without filters.')
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

        # Validate input payload
        payload, status_code = validate_request_input_against_schema(data, TestAdjustmentSchema())
        if status_code != 200:
            # If there was an error with the input payload, return the error and 422 response
            return make_response(payload, status_code)

        # All of these params can be empty, in which case, our utility functions will just return all records
        test_adj = data.get('test_adj')
        ind_se = data.get('ind_se')
        ind_sp = data.get('ind_sp')
        ind_se_n = data.get('ind_se_n')
        ind_sp_n = data.get('ind_sp_n')
        se_n = data.get('se_n')
        sp_n = data.get('sp_n')
        sensitivity = data.get('sensitivity')
        specificity = data.get('specificity')
        test_validation = data.get('test_validation')
        test_type = data.get('test_type')
        denominator_value = data.get('denominator_value')
        serum_pos_prevalence = data.get('serum_pos_prevalence')

        # Apply test adjustment
        multiprocessing.set_start_method("fork")
        test_adj_handler = TestAdjHandler()
        adj_prevalence, adj_sensitivity, adj_specificity, ind_eval_type, adj_prev_ci_lower, adj_prev_ci_upper = \
            test_adj_handler.get_adjusted_estimate(test_adj, ind_se, ind_sp, ind_se_n, ind_sp_n, se_n, sp_n,
                                                   sensitivity, specificity, test_validation, test_type,
                                                   denominator_value, serum_pos_prevalence)

        # Return result as json payload
        result = {"adj_prevalence": adj_prevalence,
                  "adj_sensitivity": adj_sensitivity,
                  "adj_specificity": adj_specificity,
                  "ind_eval_type": ind_eval_type,
                  "adj_prev_ci_lower": adj_prev_ci_lower,
                  "adj_prev_ci_upper": adj_prev_ci_upper}
        return jsonify(result)
