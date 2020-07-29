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
FLASK_ENV=foo
AIRTABLE_API_KEY=bar
AIRTABLE_BASE_ID=baz
GMAIL_PASS=foobar
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

### Alembic

Create a file named `alembic.ini` at the top level and paste the following: 

```bash
# A generic, single database configuration.

[alembic]
# path to migration scripts
script_location = alembic

# template used to generate migration files
# file_template = %%(rev)s_%%(slug)s

# timezone to use when rendering the date
# within the migration file as well as the filename.
# string value is passed to dateutil.tz.gettz()
# leave blank for localtime
# timezone =

# max length of characters to apply to the
# "slug" field
# truncate_slug_length = 40

# set to 'true' to run the environment during
# the 'revision' command, regardless of autogenerate
# revision_environment = false

# set to 'true' to allow .pyc and .pyo files without
# a source .py file to be detected as revisions in the
# versions/ directory
# sourceless = false

# version location specification; this defaults
# to alembic/versions.  When using multiple version
# directories, initial revisions must be specified with --version-path
# version_locations = %(here)s/bar %(here)s/bat alembic/versions

# the output encoding used when revision files
# are written from script.py.mako
# output_encoding = utf-8

sqlalchemy.url = postgresql://{USERNAME}:{PASSWORD}@localhost:5432/whiteclaw

[post_write_hooks]
# post_write_hooks defines scripts or Python functions that are run
# on newly generated revision scripts.  See the documentation for further
# detail and examples

# format using "black" - use the console_scripts runner, against the "black" entrypoint
# hooks=black
# black.type=console_scripts
# black.entrypoint=black
# black.options=-l 79

# Logging configuration
[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
```

### Populate local database

Run the script `python app/database_etl/etl_main.py`.

Confirm that the data has indeed been migrated by checking pgAdmin 4.
