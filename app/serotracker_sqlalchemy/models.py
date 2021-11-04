from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID

from app import db


# Dashboard table for all dashboard fields
class DashboardSource(db.Model):
    __tablename__ = 'dashboard_source'

    source_id = Column(UUID(as_uuid=True), primary_key=True)
    source_name = Column(String())
    publication_date = Column(DateTime)
    first_author = Column(String())
    url = Column(String())
    source_type = Column(String())
    source_publisher = Column(String())
    summary = Column(String())
    study_name = Column(String())
    study_type = Column(String())
    country_id = Column(UUID(as_uuid=True))
    lead_organization = Column(String())
    sampling_start_date = Column(DateTime)
    sampling_end_date = Column(DateTime)
    age = Column(String())
    sex = Column(String())
    population_group = Column(String())
    sampling_method = Column(String())
    sensitivity = Column(Float)
    specificity = Column(Float)
    included = Column(Boolean)
    denominator_value = Column(Integer)
    numerator_definition = Column(String())
    serum_pos_prevalence = Column(Float)
    overall_risk_of_bias = Column(String())
    isotype_igg = Column(Boolean)
    isotype_igm = Column(Boolean)
    isotype_iga = Column(Boolean)
    specimen_type = Column(String())
    estimate_grade = Column(String())
    academic_primary_estimate = Column(Boolean)
    dashboard_primary_estimate = Column(Boolean)
    isotype_comb = Column(String())
    test_type = Column(String())
    test_adj = Column(Boolean)
    pop_adj = Column(Boolean)
    created_at = Column(DateTime)
    cases_per_hundred = Column(Float)
    tests_per_hundred = Column(Float)
    deaths_per_hundred = Column(Float)
    vaccinations_per_hundred = Column(Float)
    full_vaccinations_per_hundred = Column(Float)
    vaccination_policy = Column(String())
    geo_exact_match = Column(Boolean)
    adj_prevalence = Column(Float)
    adj_prev_ci_lower = Column(Float)
    adj_prev_ci_upper = Column(Float)
    pin_latitude = Column(Float)
    pin_longitude = Column(Float)
    in_disputed_area = Column(Boolean)
    subgroup_var = Column(String())
    is_unity_aligned = Column(Boolean)


# Research table for all additional research fields
class ResearchSource(db.Model):
    __tablename__ = 'research_source'

    source_id = Column(UUID(as_uuid=True), primary_key=True)
    case_population = Column(Integer)
    deaths_population = Column(Integer)
    age_max = Column(Float)
    age_min = Column(Float)
    age_variation = Column(String())
    age_variation_measure = Column(String())
    average_age = Column(String())
    case_count_neg14 = Column(Integer)
    case_count_neg9 = Column(Integer)
    case_count_0 = Column(Integer)
    date_created = Column(DateTime)
    death_count_plus11 = Column(Integer)
    death_count_plus4 = Column(Integer)
    include_in_srma = Column(Boolean)
    sensspec_from_manufacturer = Column(Boolean)
    ind_eval_lab = Column(String())
    ind_eval_link = Column(String())
    ind_se = Column(Float)
    ind_se_n = Column(Float)
    ind_sp = Column(Float)
    ind_sp_n = Column(Float)
    jbi_1 = Column(String())
    jbi_2 = Column(String())
    jbi_3 = Column(String())
    jbi_4 = Column(String())
    jbi_5 = Column(String())
    jbi_6 = Column(String())
    jbi_7 = Column(String())
    jbi_8 = Column(String())
    jbi_9 = Column(String())
    jbi_a_outputs_v5 = Column(String())
    last_modified_time = Column(DateTime)
    measure_of_age = Column(String())
    sample_frame_info = Column(String())
    number_of_females = Column(Integer)
    number_of_males = Column(Integer)
    numerator_value = Column(Float)
    estimate_name = Column(String())
    test_not_linked_reason = Column(String())
    se_n = Column(Float)
    seroprev_95_ci_lower = Column(Float)
    seroprev_95_ci_upper = Column(Float)
    sp_n = Column(Float)
    subgroup_cat = Column(String())
    subgroup_specific_category = Column(String())
    test_name = Column(String())
    test_validation = Column(String())
    multiple_test_gold_standard_algorithm = Column(String())
    gbd_region = Column(String())
    gbd_subregion = Column(String())
    who_region = Column(String())
    lmic_hic = Column(String())
    genpop = Column(String())
    sampling_type = Column(String())
    airtable_record_id = Column(String())
    adj_sensitivity = Column(Float)
    adj_specificity = Column(Float)
    ind_eval_type = Column(String())
    created_at = Column(DateTime)
    zotero_citation_key = Column(String())
    county = Column(String())


# Create base multi select tables
class Country(db.Model):
    __tablename__ = 'country'

    country_id = Column(UUID(as_uuid=True), primary_key=True)
    country_name = Column(String())
    country_iso3 = Column(String())
    country_iso2 = Column(String())
    latitude = Column(Float)
    longitude = Column(Float)
    hrp_class = Column(String())
    income_class = Column(String())
    created_at = Column(DateTime)


class City(db.Model):
    __tablename__ = 'city'

    city_id = Column(UUID(as_uuid=True), primary_key=True)
    city_name = Column(String())
    latitude = Column(Float)
    longitude = Column(Float)
    created_at = Column(DateTime)
    # The columns below are not needed for our endpoints but are helpful
    # when debugging latlng assignment
    state_name = Column(String())
    country_iso2 = Column(String())


class State(db.Model):
    __tablename__ = 'state'

    state_id = Column(UUID(as_uuid=True), primary_key=True)
    state_name = Column(String())
    latitude = Column(Float)
    longitude = Column(Float)
    created_at = Column(DateTime)
    # The columns below are not needed for our endpoints but are helpful
    # when debugging latlng assignment
    country_iso2 = Column(String())


class TestManufacturer(db.Model):
    __tablename__ = 'test_manufacturer'

    test_manufacturer_id = Column(UUID(as_uuid=True), primary_key=True)
    test_manufacturer_name = Column(String())
    created_at = Column(DateTime)


class AntibodyTarget(db.Model):
    __tablename__ = 'antibody_target'

    antibody_target_id = Column(UUID(as_uuid=True), primary_key=True)
    antibody_target_name = Column(String())
    created_at = Column(DateTime)


# Create bridge tables
class CityBridge(db.Model):
    __tablename__ = 'city_bridge'

    id = Column(UUID(as_uuid=True), primary_key=True)
    source_id = Column(UUID(as_uuid=True))
    city_id = Column(UUID(as_uuid=True))
    created_at = Column(DateTime)


class StateBridge(db.Model):
    __tablename__ = 'state_bridge'

    id = Column(UUID(as_uuid=True), primary_key=True)
    source_id = Column(UUID(as_uuid=True))
    state_id = Column(UUID(as_uuid=True))
    created_at = Column(DateTime)


class TestManufacturerBridge(db.Model):
    __tablename__ = 'test_manufacturer_bridge'

    id = Column(UUID(as_uuid=True), primary_key=True)
    source_id = Column(UUID(as_uuid=True))
    test_manufacturer_id = Column(UUID(as_uuid=True))
    created_at = Column(DateTime)


class AntibodyTargetBridge(db.Model):
    __tablename__ = 'antibody_target_bridge'

    id = Column(UUID(as_uuid=True), primary_key=True)
    source_id = Column(UUID(as_uuid=True))
    antibody_target_id = Column(UUID(as_uuid=True))
    created_at = Column(DateTime)


class PopulationGroupOptions(db.Model):
    __tablename__ = 'population_group_options'

    id = Column(UUID(as_uuid=True), primary_key=True)
    name = Column(String())
    french_name = Column(String())
    order = Column(Integer)
    created_at = Column(DateTime)
