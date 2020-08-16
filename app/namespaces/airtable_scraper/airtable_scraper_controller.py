
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
