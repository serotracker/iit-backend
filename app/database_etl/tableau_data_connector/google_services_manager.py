from __future__ import print_function
import os
import pickle

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError, BatchError
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from app.utils import send_slack_message


class GoogleSheetsManager:
    def __init__(self):
        self.scope = ['https://www.googleapis.com/auth/spreadsheets']
        self.range = 'A1:ZZ10000'
        self.client_service = self.create_service()
        return

    def create_service(self):
        creds = None
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)

            # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', self.scope)
                creds = flow.run_local_server(port=0)

            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
        service = build('sheets', 'v4', credentials=creds)
        return service

    def clear_sheet(self, spreadsheet_id):
        sheet = self.client_service.spreadsheets()
        sheet.values().clear(spreadsheetId=spreadsheet_id, range=self.range).execute()
        return

    def update_sheet(self, spreadsheet_id, df):
        sheet = self.client_service.spreadsheets()
        batch_update_values_request_body = {'valueInputOption': 'RAW',
                                            'data': {'range': self.range,
                                                     'majorDimension': 'ROWS',
                                                     'values': df.T.reset_index().T.values.tolist()}}
        self.clear_sheet(spreadsheet_id)
        try:
            sheet.values().batchUpdate(spreadsheetId=spreadsheet_id,
                                       body=batch_update_values_request_body).execute()
        except (HttpError, BatchError) as e:
            body = f'Error loading Tableau CSV to google sheets: {e}'
            send_slack_message(body, channel='#dev-logging-etl')
        return
