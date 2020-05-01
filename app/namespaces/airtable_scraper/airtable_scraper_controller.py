import os
from datetime import datetime

from flask_restplus import Resource, Namespace
from flask import jsonify, current_app as app

from .airtable_scraper_service import get_all_records, write_to_json, read_from_json

airtable_scraper_ns = Namespace('airtable_scraper', description='An endpoint for scraping airtable data.')


@airtable_scraper_ns.route('/records', methods=['GET'])
class AirtableScraper(Resource):
    @airtable_scraper_ns.doc('An endpoint for getting all records of airtable data.')
    def get(self):
        try:
            current_time = datetime.now()
            file_created_time = datetime.fromtimestamp(os.path.getmtime('cached_results.json'))
            hour_diff = ((current_time - file_created_time).total_seconds())/3600
            generate_new_cache = True if hour_diff > app.config['TIME_DIFF'] else False
        except FileNotFoundError:
            generate_new_cache = True
        if generate_new_cache:
            records = get_all_records()
            write_to_json(records)
        else:
            records = read_from_json()
        return jsonify(records)


