# iit-backend
Server side code for the International Immunity Tracker

### Setup
After cloning, add a `.env` file to the top level of the repository to store environment variables. This file should be formatted as follows:
```bash
FLASK_ENV=foo
AIRTABLE_API_KEY=bar
AIRTABLE_BASE_ID=baz
GMAIL_PASS=foobar
```

### Run airtable_fields_config.json
If there are changes to the Airtable schema, the `airtable_fields_config.json` found in app/utils must be regenerated.
1. Download the Airtable SOP sheet from the Google Drive as a csv and put it in app/utils.
2. Remove the first few lines of the csv, so that the first line contains the columns of the table:
'#, Column Label, DB?, ShortName, Data Type, Description'.
3. Run `airtable_fields_config_handler.py` in app/utils. This script takes --file_name as an argument,
which is the name of the Airtable CSV. The default is `"Airtable SOP.csv"`.
4. Once you have run the script, you should see the new `airtable_fields_config.json` in app/utils.
