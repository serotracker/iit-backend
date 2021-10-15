dashboard_fields = ['Source Name', 'Publication Date', 'First Author Full Name', 'Organizational Author', 'URL',
                    'Source Type', 'Source Publisher', 'One-Line Summary', 'Study Type', 'Country',
                    'Lead Organization', 'State/Province', 'City', 'Sampling Start Date', 'Sampling End Date',
                    'Sample Frame (sex)', 'Sample Frame (age)', 'Sample Frame (groups of interest)', 'Sampling Method',
                    'Test Manufacturer', 'Test Type', 'Specimen Type', 'Isotype(s) Reported', 'Sub-grouping Variable',
                    'Sensitivity', 'Specificity', 'Included?', 'Denominator Value', 'Numerator Definition',
                    'Serum positive prevalence', 'Overall Risk of Bias (JBI)', 'Grade of Estimate Scope',
                    'SeroTracker Analysis Primary Estimate', 'Most Adjusted Primary Estimate', 'Isotype combination',
                    'Rapid Review Study Name (Text)', 'Test Adjustment', 'Population Adjustment', 'UNITY: Criteria']

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
                   'Sub-group specific category (clean)', 'Date Created', 'Last modified time', 'Record ID',
                   'SR Clean: Test Manufacturer Searched', 'Zotero Citation Key', 'County']

full_airtable_fields = {'2020 Population Count - Case': 'case_population',
                        '2020 Population Count - Mortality': 'deaths_population',
                        'SeroTracker Analysis Primary Estimate': 'academic_primary_estimate',
                        'Adjusted sensitivity': 'adj_sensitivity',
                        'Adjusted serum positive prevalence': 'adj_prevalence',
                        'Adjusted serum pos prevalence, 95pct CI Lower': 'adj_prev_ci_lower',
                        'Adjusted serum pos prevalence, 95pct CI Upper': 'adj_prev_ci_upper',
                        'Adjusted specificity': 'adj_specificity',
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
                        'Most Adjusted Primary Estimate': 'dashboard_primary_estimate',
                        'Date Created': 'date_created',
                        'Denominator Value': 'denominator_value',
                        'First Author Full Name': 'first_author',
                        'Grade of Estimate Scope': 'estimate_grade',
                        'Included?': 'included',
                        'included in SRMA (mar 2021)': 'include_in_srma',
                        'Independent Eval Lab': 'ind_eval_lab',
                        'Independent Eval Link': 'ind_eval_link',
                        'Independent evaluation type': 'ind_eval_type',
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
                        'SR Clean: Test Manufacturer Searched': 'sensspec_from_manufacturer',
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
                        'UNITY: Criteria': 'is_unity_aligned',
                        'URL': 'url',
                        'Zotero Citation Key': 'zotero_citation_key'}

airtable_fields_config = {'dashboard': {k: full_airtable_fields[k] for k in dashboard_fields},
                          'research': {k: full_airtable_fields[k] for k in research_fields}}