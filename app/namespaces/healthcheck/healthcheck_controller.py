from flask import jsonify
from flask_restplus import Resource, Namespace

healthcheck_ns = Namespace('healthcheck', description='A health check endpoint.')


@healthcheck_ns.route('/', methods=['GET'])
class Healthcheck(Resource):
    @healthcheck_ns.doc('A health check endpoint.')
    def get(self):
        response = 'The healthcheck endpoint was hit.'
        return jsonify(response)
