import os
from datetime import datetime

from flask_restplus import Resource, Namespace
from flask import jsonify, current_app as app

from app.utils import get_filtered_records, get_paginated_records

records_ns =\
    Namespace('records', description='An endpoint for getting records from the database.')

@records_ns.route('/records', methods=['POST'])
class Records(Resource):
    @records_ns.doc('An endpoint for getting all records from database')
    def post(self): 
        data = reequest.form

        # All of these params can be empty, in which case, our utility functions will just return all records
        filters = data.get('filters')
        sorting_key = data.get('page_sorting_key')
        page_index = data.get('page_index')
        per_page = data.get('per_page')

        filtered_records = get_filtered_records(filters)
        result = get_paginated_records(filtered_records, sorting_key, page_index, per_page)

        return jsonify(result)


