dashboard_fields = ['Source Name', 'Publication Date', 'First Author Full Name', 'Organizational Author', 'URL',
                    'Source Type', 'Source Publisher', 'One-Line Summary', 'Study Type', 'Country',
                    'Lead Organization', 'State/Province', 'City', 'County', 'Sampling Start Date', 'Sampling End Date',
                    'Sample Frame (sex)', 'Sample Frame (age)', 'Sample Frame (groups of interest)', 'Sampling Method',
                    'Test Manufacturer', 'Test Type', 'Specimen Type', 'Isotype(s) Reported', 'Sub-grouping Variable',
                    'Sensitivity', 'Specificity', 'Included?', 'Denominator Value', 'Numerator Definition',
                    'Serum positive prevalence', 'Overall Risk of Bias (JBI)', 'Grade of Estimate Scope',
                    'Academic Primary Estimate', 'Dashboard Primary Estimate', 'Isotype combination',
                    'Rapid Review Study Name (Text)', 'Test Adjustment', 'Population Adjustment']

research_fields = ['2020 Population Count - Case', '2020 Population Count - Mortality', 'Age Maximum', 'Age Minimum',
                   'Age variation', 'Age variation measure', 'Antibody target', 'Average age',
                   'Cumulative Case Count on -14 Days from End Date', 'Cumulative Case Count on -9 days from End Date',
                   'Cumulative Case Count on End Date', 'Cumulative Covid Mortality Count on plus11 Days from End Date',
                   'Cumulative Covid Mortality Count on plus4 Days from End Date', 'Independent Eval Lab',
                   'Independent Eval Link', 'Independent Se', 'Independent Se n', 'Independent Sp', 'Independent Sp n',
                   'JBI 1', 'JBI 2', 'JBI 3', 'JBI 4', 'JBI 5', 'JBI 6', 'JBI 7', 'JBI 8', 'JBI 9', 'Measure of age',
                   'Notes on Sample Frame', 'Number of females', 'Number of males', 'Numerator Value',
                   'Prevalence Estimate Name', 'Reason for no test link', 'Sensitivity Denominator',
                   'Serum pos prevalence, 95pct CI Lower', 'Serum pos prevalence, 95pct CI Upper',
                   'Specificity Denominator', 'Subgroup category for analysis',
                   'Test Link Unique ID', 'Test Name', 'Test Validation', 'included in SRMA (mar 2021)',
                   'Sub-group specific category (clean)', 'Date Created', 'Last modified time', 'Record ID']

full_airtable_fields = {'2020 Population Count - Case': 'case_population',
                        '2020 Population Count - Mortality': 'deaths_population',
                        'Academic Primary Estimate': 'academic_primary_estimate',
                        'Age Maximum': 'age_max',
                        'Age Minimum': 'age_min',
                        'Age variation': 'age_variation',
                        'Age variation measure': 'age_variation_measure',
                        'Antibody target': 'antibody_target',
                        'Average age': 'average_age',
                        'City': 'city',
                        'Country': 'country',
                        'County': 'county',
                        'Cumulative Case Count on -14 Days from End Date': 'case_count_neg14',
                        'Cumulative Case Count on -9 days from End Date': 'case_count_neg9',
                        'Cumulative Case Count on End Date': 'case_count_0',
                        'Cumulative Covid Mortality Count on plus11 Days from End Date': 'death_count_plus11',
                        'Cumulative Covid Mortality Count on plus4 Days from End Date': 'death_count_plus4',
                        'Dashboard Primary Estimate': 'dashboard_primary_estimate',
                        'Date Created': 'date_created',
                        'Denominator Value': 'denominator_value',
                        'First Author Full Name': 'first_author',
                        'Grade of Estimate Scope': 'estimate_grade',
                        'Included?': 'included',
                        'included in SRMA (mar 2021)': 'include_in_srma',
                        'Independent Eval Lab': 'ind_eval_lab',
                        'Independent Eval Link': 'ind_eval_link',
                        'Independent Se': 'ind_se',
                        'Independent Se n': 'ind_se_n',
                        'Independent Sp': 'ind_sp',
                        'Independent Sp n': 'ind_sp_n',
                        'Isotype combination': 'isotype_comb',
                        'Isotype(s) Reported': 'isotypes',
                        'JBI 1': 'jbi_1',
                        'JBI 2': 'jbi_2',
                        'JBI 3': 'jbi_3',
                        'JBI 4': 'jbi_4',
                        'JBI 5': 'jbi_5',
                        'JBI 6': 'jbi_6',
                        'JBI 7': 'jbi_7',
                        'JBI 8': 'jbi_8',
                        'JBI 9': 'jbi_9',
                        'Last modified time': 'last_modified_time',
                        'Lead Organization': 'lead_organization',
                        'Measure of age': 'measure_of_age',
                        'Notes on Sample Frame': 'sample_frame_info',
                        'Number of females': 'number_of_females',
                        'Number of males': 'number_of_males',
                        'Numerator Definition': 'numerator_definition',
                        'Numerator Value': 'numerator_value',
                        'One-Line Summary': 'summary',
                        'Organizational Author': 'organizational_author',
                        'Overall Risk of Bias (JBI)': 'overall_risk_of_bias',
                        'Population Adjustment': 'pop_adj',
                        'Prevalence Estimate Name': 'estimate_name',
                        'Publication Date': 'publication_date',
                        'Rapid Review Study Name (Text)': 'study_name',
                        'Reason for no test link': 'test_not_linked_reason',
                        'Record ID': 'airtable_record_id',
                        'Sample Frame (age)': 'age',
                        'Sample Frame (groups of interest)': 'population_group',
                        'Sample Frame (sex)': 'sex',
                        'Sampling End Date': 'sampling_end_date',
                        'Sampling Method': 'sampling_method',
                        'Sampling Start Date': 'sampling_start_date',
                        'Sensitivity': 'sensitivity',
                        'Sensitivity Denominator': 'se_n',
                        'Serum pos prevalence, 95pct CI Lower': 'seroprev_95_ci_lower',
                        'Serum pos prevalence, 95pct CI Upper': 'seroprev_95_ci_upper',
                        'Serum positive prevalence': 'serum_pos_prevalence',
                        'Source Name': 'source_name',
                        'Source Publisher': 'source_publisher',
                        'Source Type': 'source_type',
                        'Specificity': 'specificity',
                        'Specificity Denominator': 'sp_n',
                        'Specimen Type': 'specimen_type',
                        'State/Province': 'state',
                        'Study Type': 'study_type',
                        'Sub-group specific category (clean)': 'subgroup_specific_category',
                        'Sub-grouping Variable': 'subgroup_var',
                        'Subgroup category for analysis': 'subgroup_cat',
                        'Test Adjustment': 'test_adj',
                        'Test Link Unique ID': 'test_linked_uid',
                        'Test Manufacturer': 'test_manufacturer',
                        'Test Name': 'test_name',
                        'Test Type': 'test_type',
                        'Test Validation': 'test_validation',
                        'URL': 'url'}

# Note: this is legacy code that research depends on
# We aim to clean/achieve parity on our variable naming
# in the near future!
full_airtable_fields_legacy = {
    'Source Name': 'SOURCE_NAME',
    'Publication Date': 'PUB_DATE',
    'First Author Full Name': 'FIRST_AUTHOR',
    'Organizational Author': 'ORGANIZATIONAL_AUTHOR',
    'URL': 'URL',
    'Source Type': 'SOURCE_TYPE',
    'Source Publisher': 'PUBLISHER',
    'One-Line Summary': 'SUMMARY',
    'Study Type': 'STUDY_TYPE',
    'Grade of Estimate Scope': 'ESTIMATE_GRADE',
    'Country': 'COUNTRY',
    'Lead Organization': 'LEAD_ORG',
    'State/Province': 'STATE',
    'County': 'COUNTY',
    'City': 'CITY',
    'Sampling Start Date': 'SAMPLING_START',
    'Sampling End Date': 'SAMPLING_END',
    'Sample Frame (sex)': 'SEX',
    'Sample Frame (age)': 'AGE',
    'Sample Frame (groups of interest)': 'POPULATION_GROUP',
    'Sampling Method': 'SAMPLING',
    'Test Manufacturer': 'MANUFACTURER',
    'Test Type': 'TEST_TYPE',
    'Specimen Type': 'SPECIMEN_TYPE',
    'Isotype(s) Reported': 'ISOTYPES',
    'Sensitivity': 'SENSITIVITY',
    'Specificity': 'SPECIFICITY',
    'Denominator Value': 'DENOMINATOR',
    'Numerator Definition': 'NUM_DEFINITION',
    'Serum positive prevalence': 'SERUM_POS_PREVALENCE',
    'Serum + prevalence, 95% CI Lower': 'SEROPREV_95_CI_LOWER',
    'Serum + prevalence, 95% CI Upper': 'SEROPREV_95_CI_UPPER',
    'Overall Risk of Bias (JBI)': 'OVERALL_RISK_OF_BIAS',
    'Included?': 'INCLUDED',
    'Sub-grouping Variable': 'SUBGROUP_VAR',
    'Subgroup category for analysis': 'SUBGROUP_CAT',
    'JBI 1': 'JBI_1',
    'JBI 2': 'JBI_2',
    'JBI 3': 'JBI_3',
    'JBI 4': 'JBI_4',
    'JBI 5': 'JBI_5',
    'JBI 6': 'JBI_6',
    'JBI 7': 'JBI_7',
    'JBI 8': 'JBI_8',
    'JBI 9': 'JBI_9',
    'Test Adjustment': 'TEST_ADJ',
    'Population Adjustment': 'POP_ADJ',
    'Sensitivity Denominator': 'SE_N',
    'Specificity Denominator': 'SP_N',
    'Test Validation': 'TEST_VALIDATION',
    'Independent Se': 'IND_SE',
    'Independent Se n': 'IND_SE_N',
    'Independent Sp': 'IND_SP',
    'Independent Sp n': 'IND_SP_N',
    'Independent Eval Link': 'IND_EVAL_LINK',
    'Independent Eval Lab': 'IND_EVAL_LAB',
    'Average age': 'AVERAGE_AGE',
    'Measure of age': 'MEASURE_OF_AGE',
    'Age variation': 'AGE_VARIATION',
    'Age variation measure': 'AGE_VARIATION_MEASURE',
    'Number of females': 'NUMBER_OF_FEMALES',
    'Number of males': 'NUMBER_OF_MALES',
    'Prevalence Estimate Name': 'ESTIMATE_NAME',
    'Rapid Review Study Name (Text)': 'STUDY_NAME',
    'Notes on Sample Frame': 'SAMPLE_FRAME_INFO',
    'Academic Primary Estimate': 'ACADEMIC_PRIMARY_ESTIMATE',
    'Dashboard Primary Estimate': 'DASHBOARD_PRIMARY_ESTIMATE',
    'Isotype combination': 'ISOTYPE_COMB',
    'Test Name': 'TEST_NAME',
    'Numerator Value': 'NUMERATOR_VALUE',
    'Cumulative Case Count on End Date': 'CASE_COUNT_0',
    'Cumulative Case Count on -9 days from End Date': 'CASE_COUNT_NEG9',
    'Cumulative Case Count on -14 Days from End Date': 'CASE_COUNT_NEG14',
    '2020 Population Count - Case': 'CASE_POPULATION',
    '2020 Population Count - Mortality': 'DEATHS_POPULATION',
    'Cumulative Covid Mortality Count on +4 Days from End Date': 'DEATH_COUNT_+4',
    'Cumulative Covid Mortality Count on +11 Days from End Date': 'DEATH_COUNT_+11',
    'Age Minimum': 'AGE_MIN',
    'Age Maximum': 'AGE_MAX',
    'Antibody target': 'ANTIBODY_TARGET',
    'Reason for no test link': 'TEST_NOT_LINKED_REASON',
    'Test Link Unique ID': 'TEST_LINKED_UID'
}

airtable_fields_config = {'dashboard': {k: full_airtable_fields[k] for k in dashboard_fields},
                          'research': {k: full_airtable_fields[k] for k in research_fields}}
