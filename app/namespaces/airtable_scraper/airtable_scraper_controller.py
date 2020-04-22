from flask import jsonify
from flask_restplus import Resource, Namespace

airtable_scraper_ns = Namespace('airtable_scraper', description='An endpoint for scraping airtable data.')


@airtable_scraper_ns.route('/', methods=['GET'])
class AirtableScraper(Resource):
    @airtable_scraper_ns.doc('An endpoint for getting all records of airtable data.')
    def get(self):
        return jsonify('This endpoint will eventually return all records of airtable data.')