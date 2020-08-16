
def get_country_seroprev_summaries(records):
    # Turn records into df and remove list from country
    records_df = pd.DataFrame(records)

    # Get unique list of countries
    countries = records_df.country.unique()
    study_counts_list = []

    # For each country, create a payload with all the seroprev summary info
    for country in countries:
        country_seroprev_summary_dict = {}
        country_seroprev_summary_dict['country'] = country
        records_for_country = records_df[records_df['country'] == country]

        # Get total number of seroprev estimates in country
        country_seroprev_summary_dict['n_estimates'] = records_for_country.shape[0]

        # Get total number of tests administered in country
        country_seroprev_summary_dict['n_tests_administered'] = int(records_for_country.denominator.sum())

        # Summarize seroprev estimate info at each estimate grade level
        estimate_grades = ['National', 'Regional', 'Local', 'Sublocal']
        grades_seroprev_summaries_dict = {}
        for grade in estimate_grades:
            estimate_grade_dict = {}
            records_for_grade = records_for_country[records_for_country['estimate_grade'] == grade]
            n_estimates = records_for_grade.shape[0]

            if n_estimates == 0:
                estimate_grade_dict['n_estimates'] = 0
                estimate_grade_dict['min_estimate'] = None
                estimate_grade_dict['max_estimate'] = None
            else:
                # Add number of estimates for that grade
                estimate_grade_dict['n_estimates'] = n_estimates

                # Add min and max seroprev estimates
                estimate_grade_dict['min_estimate'] = records_for_grade.serum_pos_prevalence.min()
                estimate_grade_dict['max_estimate'] = records_for_grade.serum_pos_prevalence.max()
            grades_seroprev_summaries_dict[grade] = estimate_grade_dict
        country_seroprev_summary_dict['seroprevalence_estimate_summary'] = grades_seroprev_summaries_dict
        study_counts_list.append(country_seroprev_summary_dict)
    return study_counts_list

