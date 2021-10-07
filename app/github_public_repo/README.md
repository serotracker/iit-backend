
# SARS-CoV-2 Serosurveillance Data by Serotracker

[SeroTracker](https://serotracker.com/en/Explore) synthesizes findings from thousands of COVID-19 seroprevalence studies worldwide, providing a data platform and interactive dashboard for SARS-CoV-2 serosurveillance. This dataset in this repository represents our collection of serosurveillance studies.

### Download
Our complete SARS-Cov-2 dataset can be scraped programmatically from this repository in the following ways:
1. Using the command: `curl https://raw.githubusercontent.com/serotracker/sars-cov-2-data/main/serotracker_dataset.csv` in the terminal.
2. Using a GET request through REST API protocol.

Our dataset can also be downloaded directly from our [Airtable view]([https://airtable.com/shraXWPJ9Yu7ybowM/tbljN2mhRVfSlZv2d?backgroundColor=blue&viewControls=on](https://airtable.com/shraXWPJ9Yu7ybowM/tbljN2mhRVfSlZv2d?backgroundColor=blue&viewControls=on)).

The CSV file follows the format of 1 row per estimate. 
 
### Additional Information
Please see our [Data Dictionary](https://docs.google.com/spreadsheets/d/1KQbp5T9Cq_HnNpmBTWY1iKs6Etu1-qJcnhdJ5eyw7N8/edit#gid=0) for explanations of our variables, data types, and descriptions as well as insight into how our data is collected by our research team.

In order to keep up to date with important changes to our dataset, please consult our [Change Log](https://airtable.com/shrxpAlF6v0LeRYkA/tblC6jj904WXUzwVY) regularly.

For more information about how we collect, extract and use our data, please see the [Data page](https://serotracker.com/en/Data) on our website.

If you have a SARS-CoV-2 seroprevalence study that has not yet been captured by serotracker.com, please submit the source using this [form](https://docs.google.com/forms/d/e/1FAIpQLSdvNJReektutfMT-5bOTjfnvaY_pMAy8mImpQBAW-3v7_B2Bg/viewform). Our research team will review each submission to evaluate whether it meets our inclusion criteria.

If you are open to being contacted about your use case for our data, please fill out this [form](https://forms.gle/gqi3kvKQgasYCrQE9). This helps us create datasets that are most useful to you.

Our data can be cited as this [Lancet Inf Dis article](https://www.thelancet.com/journals/laninf/article/PIIS1473-3099(20)30631-9/fulltext#%20).

### Change Log
- Oct 3, 2021: We created `serotracker_dataset.csv` containing the following columns: Prevalence Estimate Name, Publication Date, Grade of Estimate Scope, Country, Specific Geography, Sampling Start Date, Sampling End Date, Sample Frame (groups of interest), Sample Frame (age), Sub-grouping Variable, Subgroup category for analysis, Sub-group specific category, Denominator Value, Serum positive prevalence, Serum pos prevalence, 95pct CI Lower, Serum pos prevalence, 95pct CI Upper, Test Adjustment, Population Adjustment, Sampling Method, Test Manufacturer, Test Type, Isotype(s) Reported, Antibody Target, Specimen Type, Sensitivity, Specificity, Overall Risk of Bias (JBI), JBI 1, JBI 2, JBI 3, JBI 4, JBI 5, JBI 6, JBI 7, JBI 8, JBI 9, Source Type, First Author Full Name, Lead Institution, UNITY: Criteria, URL, Date Created, Last modified time, Data Quality Status.