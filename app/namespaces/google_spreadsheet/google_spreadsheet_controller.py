from flask import request
from flask_restplus import Resource, Namespace

from app.database_etl.tableau_data_connector.google_services_manager import GoogleSheetsManager

google_spreadsheet_ns = Namespace('google_spreadsheet', description='Endpoints for making changes to google sheets')


@google_spreadsheet_ns.route("/newsletter", methods=["POST"])
class AppendNewsletterSignup(Resource):
    @google_spreadsheet_ns.doc("An endpoint for adding new newslettter signups to the newsletter spreadsheet")
    def post(self):
        data = request.get_json()
        if not data:
            return {"message": "No input payload provided"}, 400

        sheet_name = "Sheet1"
        spreadsheet_id = ""
        range_name = "!A1:B1"
        values = data.get("values")

        g_client = GoogleSheetsManager(sheet_name)
        g_client.append_sheet(spreadsheet_id=spreadsheet_id, range_name=range_name, values=values)

        return {"Message": "Added email to spreadsheet"}, 200
