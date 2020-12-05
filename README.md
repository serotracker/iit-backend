# iit-backend
Server side code for the International Immunity Tracker

# Set up

## Dependencies

1. Setup pip package manager.
2. Install the virtualenv package with `pip install virtualenv`.
3. Inside the iit-backend dir, create a python virtualenv with `virtualenv .` 
4. Activate the virtualenv

    Mac: `source iit-backend/bin/activate`

    Windows: `iit-backend\Scripts\activate`

5. Install required dependents by running `pip install -r requirements.txt`

## Environment Variables

Add a `.env` file to the top level of the repository to store environment variables. This file should be formatted as follows:

```bash
FLASK_ENV=test
AIRTABLE_API_KEY=___
AIRTABLE_BASE_ID=___
GMAIL_PASS=___
PYTHONUNBUFFERED=1
DATABASE_USERNAME=___
DATABASE_PASSWORD=___
DATABASE_NAME=___
DATABASE_HOST_ADDRESS=___
MAPBOX_API_KEY=___
```

Ask someone on the Data team for the actual environment variables you'll need! 

## Postgres

1. Download and install Postgres.

    From the source: [https://www.postgresql.org/download/](https://www.postgresql.org/download/)

    Or, on a Mac: `brew install postgresql`

2. Download and install pgAdmin 4, a management tool for Postgres. 

   [https://www.pgadmin.org/download/](https://www.pgadmin.org/download/)

After installation of pgAdmin 4, launch the program. 

Verify that it was installed properly by navigating to the pgAdmin dashboard. You can do this by clicking "New pgAdmin 4 window...". (You should see the pgAdmin 4 elephant in your status bar if on Mac.) You should be brought to something like `http://127.0.0.1:63467/browser/` in your browser.

Once on the pgAdmin dashboard, create a new server named `serotracker` (right click on > Servers). Set the host name/address under the Connection tab to `localhost`. 

Inside your new server, `serotracker`, create a new database named `whiteclaw`.  

## Changing Alembic to use Flask SQLAlchemy

We are switching to use Flask migrations instead of just Alembic. Here is how to switch over:

## Delete Previous Tables & Migrations

1. Make sure you are on ```architecture-v2``` branch. We aren't merging to master yet due to
rearchitecture.
2. Drop all the tables in the ```public``` schema in your local Postgres.

  * You can do this manually by querying ```DROP TABLE public.<table_name>``` in Postgres for every table in the schema EXCEPT the
  ```alembic_version``` table (do not delete this!).

  * You can leverage the application's shell, and the attached db to drop all associated tables.

    * Run ```python manage.py shell``` in your terminal. You will need all the environment variables that
you currently use to run the app through ```python manage.py run```, so just start the shell like you
would start the app, but subsitute the ```run``` command for the ```shell``` command.

    * The application's shell should start (look's like a Python console)

    * Run ```from flask import current_app as app, db```

    * Run ```db.drop_all()```

    * Check your Postgres server to see that the only table left in the ```public``` schema is the
```alembic_version``` table.

FINALLY:
3. Delete the value of the ```version_num``` in the ```alembic_version``` table. Use
```DELETE FROM alembic_version```.

4. Delete your ```alembic``` folder where you previously stored all the migrations.

## Upgrade to Using Newest Migrations

1. Make sure you are on the latest version of the branch. You should see a folder called 
```migrations``` at the top level (same level as ```app```)

2. Move the ```alembic.ini``` file at the top level into your new ```migrations``` folder.

2. Add the following environment variables to the ```.env``` file at the top level:
* ```DATABASE_USERNAME=your_database_username```
* ```DATABASE_PASSWORD=your_database_password```
* ```DATABASE_NAME=whiteclaw```

Finally, apply the migration to upgrade your ```alembic_version``` table to the latest version, and 
recreate all the tables in the schema: ```flask db upgrade```

### Run migrations
1. In the terminal, run ```flask db upgrade```.

    This will run the migration with the most recent version code in ```migrations/versions``` and bring your database
    to the most up-to-date state with all the necessary tables.

2. Check that new tables have been created in the whitelcaw database running on your local Postgres server.

3. To revert a migration, run ```flask db downgrade```


### Populate local database

Run the script `python app/database_etl/etl_main.py`.

Confirm that the data has indeed been migrated by checking pgAdmin 4.

## Generating Airtable Fields Config from SOP
If there are changes to the Airtable schema, the `airtable_fields_config.json` found in app/utils must be regenerated.
This can be done manually, or automatically using the following steps:
1. Download the Airtable SOP sheet from the Google Drive as a csv and put it in app/utils.
2. Remove the first few lines of the csv, so that the first line contains the columns of the table:
'#, Column Label, DB?, ShortName, Data Type, Description'.
3. Run `airtable_fields_config_handler.py` in app/utils. This script takes --file_name as an argument,
which is the name of the Airtable CSV. The default is `"Airtable SOP.csv"`.
4. Once you have run the script, you should see the new `airtable_fields_config.json` in app/utils.

## Running test suite
1. Create a config in which ```FLASK_ENV=test```
2. Create an empty database called ```whiteclaw_test```
3. Run ```python manage.py test```
