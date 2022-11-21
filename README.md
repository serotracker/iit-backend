# iit-backend

Server side code for the International Immunity Tracker.

# Table of Contents

- [iit-backend](#iit-backend)
- [Table of Contents](#table-of-contents)
- [Set up](#set-up)
  - [Cloning](#cloning)
    - [WSL Recommendations](#wsl-recommendations)
  - [Environment Configuration](#environment-configuration)
    - [Using the Terminal](#using-the-terminal)
    - [Using PyCharm](#using-pycharm)
      - [PyCharm for macOS](#pycharm-for-macos)
        - [Creating a Virtual Environment](#creating-a-virtual-environment)
        - [Installing Required Packages](#installing-required-packages)
        - [Run Configuration](#run-configuration)
      - [PyCharm on Windows](#pycharm-on-windows)
        - [Anaconda](#anaconda)
        - [Creating a Virtual Environment](#creating-a-virtual-environment-1)
        - [Installing Required Packages](#installing-required-packages-1)
        - [Run Configuration](#run-configuration-1)
  - [Postgres](#postgres)
    - [Installation](#installation)
    - [Migrations](#migrations)
      - [Running migrations](#running-migrations)
      - [Creating migrations](#creating-migrations)
    - [ETL](#ETL)
  - [Running test suite](#running-test-suite)
  - [Loading Tableau CSV to Google Sheets](#loading-tableau-csv-to-google-sheets)
- [Helpful Code Snippets](#helpful-code-snippets)
  - [Working With Postgres](#working-with-postgres)
  - [Running ETL and Local Server](#running-etl-and-local-server)
  - [Export and Import](#export-and-import)
  - [Running Dockerized Flask App](#running-dockerized-flask-app)
- [Infrastructure Documentation (Current - Vanilla EC2)](#infrastructure-documentation-current---vanilla-ec2)
  - [CI/CD](#cicd)
    - [Continuous Integration](#continuous-integration)
    - [Continuous Deployment](#continuous-deployment)
    - [Results](#results)
  - [Cronjobs](#cronjobs)
  - [`tmux` sessions](#tmux-sessions)
- [Infrastructure Documentation (Future - Elastic Beanstalk)](#infrastructure-documentation-future---elastic-beanstalk)

# Set up

## Cloning

Using a terminal application, clone the repository using `git clone https://github.com/serotracker/iit-backend.git`.

### WSL Recommendations

If using Windows Subsystem for Linux (WSL) it is recommended that you clone `iit-backend` into your home directory *within* WSL. This will improve performance and Visual Studio Code compatibility. If you do this, you can still access your files using the Windows File Explorer. The following are the paths to your home directory in Windows and WSL. Here, Ubuntu is used for WSL:

- Windows: \\wsl.localhost\Ubuntu\home\<YOUR_USERNAME>
- WSL: /home/<YOUR_USERNAME>

Note that you can use `~/` as a shorthand for `/home/<YOUR_USERNAME>` e.g. `cd ~/` is equivalent to `cd /home/<YOUR_USERNAME>`.

If you plan on using Visual Studio Code as your editor, make sure to look at this [this guide](https://code.visualstudio.com/docs/remote/troubleshooting#_resolving-git-line-ending-issues-in-containers-resulting-in-many-modified-files) to avoid Git reporting a large number of modified files that have no actual differences. In short, by running `git config --global core.autocrlf input` in a WSL terminal, you can avoid a known issue where Visual Studio Code's version control tools show an excessive number of modified lines.

## Environment Configuration

### Using the Terminal

1. Setup `pip` package manager with `python -m ensurepip --upgrade`. For more details, see the official [pip documentation](https://pip.pypa.io/en/stable/installation/).
2. Install the `virtualenv` package with `pip install virtualenv`.
3. Inside the iit-backend directory, create a python virtualenv with `virtualenv .`
4. Run `touch .env` to create a `.env` file to store environment variables.
5. Use `nano .env` to format `.env` as follows (ask someone on the Data team for the actual environment variables you'll need):

```bash
PYTHONUNBUFFERED=1
FLASK_ENV=___
AIRTABLE_API_KEY=___
AIRTABLE_BASE_ID=___
GMAIL_PASS=___
DATABASE_USERNAME=___
DATABASE_PASSWORD=___
DATABASE_NAME=___
DATABASE_HOST_ADDRESS=___
MAPBOX_API_KEY=___
LOG_CONFIG_PATH=./logging.cfg
LOG_FILE_PATH=./logfile.log
SLACKBOT_TOKEN=___
ANALYZE_SPREADSHEET_ID=___
PYTHONPATH=$PYTHONPATH:$PWD:$PWD/app/
```

6. Activate the virtualenv
- Linux/WSL: `source bin/activate`
- macOS: `source venv/bin/activate`
- Windows: `Scripts\activate`

7. Load the environment variables using `set -o allexport; source .env; set +o allexport`
8. Install required dependents by running `pip install -r requirements.txt`. This step can take up to 20 minutes.
9. Run your script using `python path/to/your/script.py run`

### Using PyCharm

Install [PyCharm Community Edition](https://www.jetbrains.com/pycharm/download/).

#### PyCharm for macOS

##### Creating a Virtual Environment

In PyCharm, open iit-backend using `File > Open`.

When opening the project, PyCharm should detect the `requirements.txt` file and automatically prompt you to create a virtual environment for the project. The prompt should look like the picture below. Select your base interpreter and click `OK`. If this prompt doesn't appear, [create a virtualenv interpreter manually](https://www.jetbrains.com/help/pycharm/project-interpreter.html#3b6542ac)

![Setup Prompt Window](pictures/setup_prompt_macos.png "Setup Prompt Window")

You'll like get an error from pycharm saying that the `setup.py` file couldn't be located. You can safely ignore this message and close the prompt.

##### Installing Required Packages

Using PyCharm's built-in terminal located in the bottom lefthand side of the PyCharm window, run the command `pip install -r requirement.txt`. This will install all of the packages specified in the `requirements.txt` file in the root of the project.

##### Run Configuration

In the menu bar, select `Run > Edit Configuration`.

Click on the `+` symbol to add a new configuration and select Python. Configure as follows:

- Name: Give your configuration any name
- Script Path: select the script you want to run e.g. `manage.py` or `/app/github_public_repo/estimate_csv_creator.py`.
- Parameters: `run`
- Environment variables: Contact a team member for the complete list of environment variables
- Python interpreter: select the python virtual environment you configured above
- Interpreter options: leave blank
- Working directory: This should automatically fill based on the `Script path` value
- Add content roots to PYTHONPATH. Check this box
- Add source roots to PYTHONPATH. Check this box

Click OK.

You should now be ready to run your script!

#### PyCharm on Windows

Note that this method can work using either native Windows or WSL. However, it is **strongly** recommended that you clone the repository within your **Windows user profile** and **NOT your WSL user profile**. PyCharm WSL compatibility is only available with [PyCharm Pro Edition](https://www.jetbrains.com/help/pycharm/using-wsl-as-a-remote-interpreter.html) and the workarounds for the Community Edition are unstable and not documented here.

##### Anaconda

Install [Anaconda](https://docs.anaconda.com/anaconda/install/windows/)

##### Creating a Virtual Environment

In PyCharm, open iit-backend using `File > Open`.

When opening the project, PyCharm should detect the `requirements.txt` file and automatically prompt you to create a virtual environment for the project. This prompt does not give you all the options necessary to configure your conda environment successfully, so click *Cancel* to return to the main PyCharm window.

To create your virtual environment, open any python file (*e.g.* `manage.py`) and click on `<No interpreter>` on the bottom right of your PyCharm window. Click *Add interpreter...*

Select *Conda environment* in the lefthand side. Make sure *New environment* is selected. Give *Location* a memorable name *e.g.* iit-backend. Your configuration should look similar to the picture below.

![Setup Prompt Window](pictures/setup_prompt_windows.png "Setup Prompt Window")

Click *OK* to return to the main PyCharm window.

##### Installing Required Packages

Click *install requirements* from the yellow PyCharm prompt. If you don't see the prompt, try closing and reopening `manage.py`. This will install some of the packages using the `conda` package manager. Many packages will fail to install using `conda`, this is expected behaviour.

Next, run `conda install fiona` in the terminal (case sensitive). The terminal is located in the bottom lefthand side of the PyCharm window. `fiona` is an anaconda-specific repackaging of the `Fiona` package that allows us to skip the complicated native Windows installation process for `Fiona`.

To install the rest of the packages, use `pip` instead of `conda`. To do this, run `pip install -r requirements.txt` in the terminal.

##### Run Configuration

In the menu bar, select `Run > Edit Configuration`.

Click on the `+` symbol to add a new configuration and select Python. Configure as follows:

- Name: Give your configuration any name
- Script Path: Select the script you want to run. This could be `manage.py` or `/app/github_public_repo/estimate_csv_creator.py` or others.
- Parameters: `run`
- Environment variables: Contact a team member for the complete list of environment variables
- Python interpreter: select the conda virtual environment you configured above
- Interpreter options: leave blank
- Working directory: This should automatically fill based on the `Script path` value
- Add content roots to PYTHONPATH. Check this box
- Add source roots to PYTHONPATH. Check this box

Click OK.

You should now be ready to run your script!

## Postgres

### Installation

1. Download and install Postgres (make sure to install Postgres v11.13 as this is what we use in prod).

   From the source: [https://www.postgresql.org/download/](https://www.postgresql.org/download/)

   Or, on a Mac: `brew install postgresql`

2. Download and install pgAdmin 4, a management tool for Postgres.

   From the source: [https://www.pgadmin.org/download/](https://www.pgadmin.org/download/)

   Or, on a Mac: `brew install --cask pgadmin4`

### Migrations

#### Running migrations

1. Make sure you are on the latest version of the branch. You should see a folder called
   `migrations` at the top level (same level as `app`)

2. Move the `alembic.ini` file at the top level into your new `migrations` folder. Get the contents of
   the `alembic.ini` file from a dev team member.

3. Add the following environment variables to the `.env` file at the top level:

- `DATABASE_USERNAME=your_database_username`
- `DATABASE_PASSWORD=your_database_password`
- `DATABASE_NAME=whiteclaw`

4. Apply the migrations to upgrade your `alembic_version` to the latest version by running `flask db upgrade`. If you 
   want to revert to a previous migration version run `flask db downgrade`.

#### Creating migrations

1. Anytime you change the file `serotracker_sqlalchemy/models.py` you need to create a new migration Python file.
   To do this, run `flask db migration -m YOUR_COMMENT_YYYY_MM_DD`. The message should describe the change you have
   made to `models.py`, example: `adding_antibody_target_col_2022_05_23`.
   
2. You should see a new Python file created in `migrations/versions` that is titled with the new alembic
   version and your migration message.

### ETL

Run the script `python app/database_etl/etl_main.py`.

Confirm that the data has indeed been migrated by checking pgAdmin 4.

## Running test suite

1. Create a config in which `FLASK_ENV=test`
2. Create an empty database called `whiteclaw_test`
3. Run `python manage.py test`

## Loading Tableau CSV to Google Sheets

1. Navigate to `https://console.cloud.google.com/apis/credentials/oauthclient/702218053502-fcrju4976lt0p1dntbln2qdolo72qjki.apps.googleusercontent.com?authuser=3&project=covid-corporate--1589232879130`.
2. Make sure you are signed into the console as `can.serosurveillance.dev@gmail.com`.
3. Click `DOWNLOAD JSON` and save the file as `credentials.json` in the `tableau_data_connector` directory.
4. Run `table_generator.py` for the first time. Authenticate using `can.serosurveillance.dev@gmail.com` the first time you run this.

# Helpful Code Snippets

## Working With Postgres

- Start Postgres database: `sudo service postgresql start`
- Open Postgres interactively: `psql -h localhost -d whiteclaw -U USERNAME -w`

## Running ETL and Local Server

- Export environment variables from `.env` file into current shell: `set -o allexport; source .env; set +o allexport`
- Add path to this Flask app to your `PYTHONPATH`: `export PYTHONPATH=PATH_TO_REPO/iit-backend:$PYTHONPATH`
- Run development server: `python3 -m flask run` (without environment variables exported) or `python3 manage.py run` (with or without environment variables exported)
- Run ETL: `python3 app/database_etl/etl_main.py` (with environment variables exported and Flask app in `PYTHONPATH`)

## Restoring Database from a Dump

- Export database snapshot: `pg_dump -h localhost -U USERNAME whiteclaw -f db_dump.sql`
  - If you get an error that your postgres and pg_dump versions are incompatible, specify the exact path of pg_dump to use so it matches your postgres version
  - Example: `/usr/lib/postgresql/11/bin/pg_dump postgresql://postgres:PASSWORD@serotracker-db.cg3y9rltha9l.ca-central-1.rds.amazonaws.com/whiteclaw > db_dump.sql`
- Copy the database dump onto your local machine from the remote machine: `scp ubuntu@3.97.103.19:db_dump.sql ~`. This is the IP address corresponding to our machine
  that runs the Flask app. This will copy the file into your local directory `~`.
- Wipe the existing database:
  - Enter postgres interactively as the `postgres` user: `psql -U postgres -h localhost -W`
  - Drop the database: `drop database whiteclaw;`
  - Create the database: `create database whiteclaw;`
- Restore the snapshot: `psql -h localhost -U USERNAME whiteclaw < db_dump.sql`

## Running Dockerized Flask App

- Prerequisite: Setup docker and docker desktop (optional). Use the following link if you have an M1 Mac (https://docs.docker.com/docker-for-mac/apple-silicon/)

- `cd` into the root of this repo
- Create a database dump and save it to `docker_postgres_dump.sql` using `pg_dump --create -h localhost -U <USERNAME> whiteclaw -f docker_postgres_dump.sql`
- Make sure you have the appropriate `.env` file at the root of this repo 
- Use the following command to set env vars based on your `.env`: `set -o allexport; source .env; set +o allexport`
- Run a cluster of containers using: `docker-compose up`. This will start a Flask app that's accessible via `localhost:5000` and a PostgreSQL instance that accessible to the Flask app.
- Shut down the cluster of containers using: `CTRL-C` followed by `docker-compose down`

---

# Infrastructure Documentation (Current - Vanilla EC2)

## CI/CD

### Continuous Integration

The following commands are run with CI:

```
pip install -r requirements.txt
python manage.py test
```

The full configuration is found [here](.github/workflows/ci.yml).

### Continuous Deployment

Deployment is conducted server-side. The documentation can be found [here](https://github.com/serotracker/scripts#update_backendsh).

### Results

Results of each job can be viewed in the Actions tab of the repository: https://github.com/serotracker/iit-backend/actions  
By default, upon a failed job, GitHub is configured to send emails to the author of the commit. To customize these notifications, refer to [GitHub Actions notification options](GitHub Actions notification options).

## Cronjobs

The backend makes use of `cron` to run jobs on a schedule.
The following tasks are executed by `cron`:

- Updating the backend
- Running the ETL
- Retrieving errors

To view/modify cronjobs run on a particular machine, run the command `crontab -e`.
This will open the `cron` file in a `vim` editor.  
In this file, each line contains one scheduled command. Refer to [this article](https://ostechnix.com/a-beginners-guide-to-cron-jobs/) to understand cronjob formatting.

For further information on `cron`, refer to the [crontab Linux manual](https://man7.org/linux/man-pages/man5/crontab.5.html).

## `tmux` sessions

A `tmux` session is an isolated environment on a machine where a process can run indefinitely. SeroTracker makes use of `tmux` sessions to run our backend servers and several scripts.  
The tmux sessions for each machine are summarized in the below table.

| Instance (IP address)  | Session name | Description                                |
| ---------------------- | ------------ | ------------------------------------------ |
| Prod (3.97.103.19)     | backend      | Run the Flask backend                      |
| Prod (3.97.103.19)     | install      | Install requirements, update the DB schema |
| Medium (35.182.41.225) | etl          | Run the ETL (once daily)                   |
| Dev (35.183.11.41)     | covidence    | Run the Covidence server                   |

### How to restore iitbackend EC2 in case of error
1. Stop instance
2. Start instance
3. Enter into prod machine
   - contact one of the dev team members for the `can_ubuntu.pem` key file
   - use the following command to ssh into the prod machine
   - `ssh -i "path to can_ubuntu.pem file" ubuntu@<prod machine ip addres>`
   - e.g. `ssh -i "can_ubuntu.pem" ubuntu@3.97.103.19`
4. Cd into www/iit-backend
5. Start new session with name: tmux new -s backend
6. Enter into venv in tmux session: source venv/bin/activate
7. Load .env into environment variables: cd into www/iit-backend and run “set -o allexport; source .env; set +o allexport”
8. Restart backend: cd ~/bin and update_backend
# Infrastructure Documentation (Future - Elastic Beanstalk)

See https://docs.google.com/document/d/1sItF1-I8uhfz9kQX62x2RooS4BndqnDBXH9g9TAWss0/edit#
