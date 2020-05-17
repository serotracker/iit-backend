import json
import argparse

import pandas as pd


def create_airtable_fields_config_from_csv(csv_file):
    try:
        # Read csv indicating which Airtable columns to pull
        airtable_config_df = pd.read_csv(csv_file)

        # Only keep Airtable rows where 'DB?' is 'Y' because they should be pulled by app
        airtable_config_df = airtable_config_df[airtable_config_df['DB?'] == 'Y']
        airtable_config_df = airtable_config_df[['Column Label', 'ShortName']]

        # Create config dict based on column label and shortname columns
        column_label = airtable_config_df['Column Label'].tolist()
        short_name = airtable_config_df['ShortName'].tolist()
        config_dict = {column_label[i]: short_name[i] for i in range(len(column_label))}

        # Create config json from config dict in app/utils
        with open('airtable_fields_config.json', 'w') as f:
            json.dump(config_dict, f)
        return
    except FileNotFoundError:
        print("Please enter a valid name for the Airtable config CSV stored in app/utils.")
        exit()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file_name',
                        default='Airtable SOP.csv',
                        help='Name of CSV file with Airtable db model stored in app/utils.')
    args = parser.parse_args()
    create_airtable_fields_config_from_csv(args.file_name)
