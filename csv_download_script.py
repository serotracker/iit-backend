import pandas as pd 
import requests
import collections
import os

AIRTABLE_API_KEY = os.getenv('AIRTABLE_API_KEY')

headers = {'Authorization': 'Bearer {}'.format(AIRTABLE_API_KEY)}
url = "https://api.airtable.com/v0/appFfYIupTrVQ0HJx/Rapid%20Review%3A%20Estimates?view=SeroTracker:%20Serosurveys%20Reporting%20Prevalence"


wanted_fields = ['Prevalence%20Estimate%20Name', 'Publication%20Date', "Grade%20of%20Estimate%20Scope", "Country", 
                    "Specific%20Geography", "Sampling%20Start%20Date", "Sampling%20End%20Date", "Sample%20Frame%20(groups%20of%20interest)", 
                    "Sample%20Frame%20(age)", "Denominator%20Value", "Serum%20positive%20prevalence", "Serum%20pos%20prevalence,%2095pct%20CI%20Upper", 
                    "Serum%20pos%20prevalence, 95pct%20CI%20Lower", "Sampling%20Method", "Test%20Manufacturer", "Test%20Type", "Isotype(s)%20Reported",
                    "Sensitivity%20(from%20Test%20Evaluation%20lookup)", "Specificity%20(from%20Test%20Evaluation%20lookup)", "Overall%20Risk%20of%20Bias%20(JBI)",
                    "Source%20Type", "First%20Author%20Full Name", "Lead%20Institution", "URL", "Date%20Created", "Last%20modified%20time", "Data%20Quality%20Status"]

# Adding all wanted fields as query params to URL
for wanted_field in wanted_fields:
    url += "&fields=" + wanted_field

organized_data = collections.defaultdict(list)
offset = ""

print("Starting CSV download...")

while True:
    # Add offset as query param to URL if there is a valid offset
    new_url = url + "&offset=" + offset
    r = requests.get(new_url, headers=headers)
    data = r.json()
    # Organize records with ID as primary key
    for record in data['records']:
        organized_data[record['id']] = record['fields']
    # Update offset if there is another page
    if "offset" in data:
        offset = data['offset']
    else:
        break
    
# Put into dataframe
df = pd.DataFrame.from_dict(organized_data, orient="index")

# Output to a csv file 
df.to_csv("serotracker_data_download.csv")

print("CSV downloaded succesfully!")

