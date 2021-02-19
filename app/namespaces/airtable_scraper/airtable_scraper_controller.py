import os
from datetime import datetime

from flask_restplus import Resource, Namespace
from flask import jsonify, request, make_response, current_app as app

from .airtable_scraper_service import get_all_records, get_country_seroprev_summaries
from .airtable_scraper_schema import StudyCountSchema
from app.utils import write_to_json, read_from_json, validate_request_input_against_schema

airtable_scraper_ns = Namespace('airtable_scraper', description='An endpoint for scraping airtable data.')


@airtable_scraper_ns.route('/records', methods=['GET'])
class AirtableScraper(Resource):
    @airtable_scraper_ns.doc('An endpoint for getting all records of airtable data.')
    def get(self):
        # Parse request parameters
        visualize_on_serotracker_filter = request.args.get('visualize_on_serotracker_filter', 1, type=int)
        airtable_fields_json_name = request.args.get('airtable_fields_json_name', 'dashboard')

        # Only check cache if records are being pulled for dashboard
        if airtable_fields_json_name == 'dashboard':
            try:
                # Check how long it has been since cached_results.json was last updated
                current_time = datetime.now()
                file_created_datetime =\
                    datetime.fromtimestamp(os.path.getmtime(app.config['AIRTABLE_CACHED_RESULTS_PATH']))
                hour_diff = ((current_time - file_created_datetime).total_seconds())/3600
                # If longer than value of time diff param, generate a new cache
                generate_new_cache = True if hour_diff > app.config['AIRTABLE_TIME_DIFF'] else False
            except FileNotFoundError:
                # If cached_results.json has never been created, generate a new cache
                generate_new_cache = True
                file_created_datetime = datetime.now()
            if generate_new_cache:
                # Get all records from using airtable API
                records, status_code = get_all_records(airtable_fields_json_name)
                if status_code == 200:
                    # Write new records to json only if the airtable API request was successful
                    write_to_json(records, app.config['AIRTABLE_CACHED_RESULTS_PATH'])
            else:
                # Read records from json cache layer
                records = read_from_json(app.config['AIRTABLE_CACHED_RESULTS_PATH'])
                status_code = 200

        # If records aren't being pulled for dashboard, make new request and don't write to cache
        else:
            # Get all records from using airtable API
            records, status_code = get_all_records(airtable_fields_json_name)
            file_created_datetime = datetime.now()

        max_pub_date = datetime.min
        for record in records:
            if record["PUB_DATE"] is not None:
                d = datetime.strptime(record["PUB_DATE"][0], '%Y-%m-%d')
                if d > max_pub_date:
                    max_pub_date = d
        max_pub_date = max_pub_date.strftime('%Y-%m-%d')

        result = {"airtable_request_status_code": status_code, "records": records, "updated_at": max_pub_date}
        return jsonify(result)


@airtable_scraper_ns.route('/country_seroprev_summary', methods=['POST'])
class GeogStudyCount(Resource):
    @airtable_scraper_ns.doc('An endpoint for summarizing the seroprevalence data of a country.')
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
