from app.serotracker_sqlalchemy import CityBridge, City, StateBridge, State, \
    TestManufacturerBridge, TestManufacturer, AntibodyTargetBridge, AntibodyTarget

db_model_config = {
    'multi_select_columns': ['test_manufacturer', 'city', 'state', 'antibody_target'],
    'supplementary_table_info': [
        {
            "bridge_table": CityBridge,
            "main_table": City,
            "entity": "city"
        },
        {
            "bridge_table": StateBridge,
            "main_table": State,
            "entity": "state"
        },
        {
            "bridge_table": TestManufacturerBridge,
            "main_table": TestManufacturer,
            "entity": "test_manufacturer"
        },
        {
            "bridge_table": AntibodyTargetBridge,
            "main_table": AntibodyTarget,
            "entity": "antibody_target"
        }
    ]
}

db_tables = ['airtable_source',
             'city',
             'city_bridge',
             'state',
             'state_bridge',
             'test_manufacturer',
             'test_manufacturer_bridge']

dashboard_source_cols = ['source_name', 'source_type', 'study_name', 'denominator_value',
                         'overall_risk_of_bias', 'serum_pos_prevalence', 'isotype_igm', 'isotype_iga',
                         'isotype_igg', 'sex', 'age', 'sampling_start_date', 'sampling_end_date', 'estimate_grade',
                         'isotype_comb', 'academic_primary_estimate', 'dashboard_primary_estimate', 'pop_adj',
                         'test_adj', 'specimen_type', 'test_type', 'population_group', 'url', 'cases_per_hundred',
                         'tests_per_hundred', 'deaths_per_hundred', 'vaccinations_per_hundred',
                         'full_vaccinations_per_hundred', 'publication_date', 'geo_exact_match',
                         'sensitivity', 'specificity', 'summary', 'study_type', 'source_publisher', 'lead_organization',
                         'first_author', 'adj_prevalence', 'adj_prev_ci_lower', 'adj_prev_ci_upper']

research_source_cols = ['case_population', 'deaths_population', 'age_max', 'age_min', 'age_variation',
                        'age_variation_measure', 'average_age', 'case_count_neg14', 'case_count_neg9',
                        'case_count_0', 'death_count_plus11', 'death_count_plus4', 'ind_eval_lab',
                        'ind_eval_link', 'ind_se', 'ind_se_n', 'ind_sp', 'ind_sp_n', 'jbi_1', 'jbi_2',
                        'jbi_3', 'jbi_4', 'jbi_5', 'jbi_6', 'jbi_7', 'jbi_8', 'jbi_9', 'measure_of_age',
                        'sample_frame_info', 'number_of_females', 'number_of_males', 'numerator_value',
                        'estimate_name', 'test_not_linked_reason', 'se_n', 'seroprev_95_ci_lower',
                        'seroprev_95_ci_upper', 'sp_n', 'subgroup_var', 'subgroup_cat',
                        'test_linked_uid', 'test_name', 'test_validation', 'gbd_region', 'gbd_subregion',
                        'lmic_hic', 'genpop', 'sampling_type', 'subgroup_specific_category', 'last_modified_time',
                        'date_created', 'adj_sensitivity', 'adj_specificity', 'ind_eval_type', 'include_in_srma']
