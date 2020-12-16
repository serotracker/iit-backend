from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID

from app import db


# Dashboard table for all dashboard fields
class DashboardSource(db.Model):
    __tablename__ = 'dashboard_source'

    source_id = Column(UUID(as_uuid=True), primary_key=True)
    source_name = Column(String())
    publication_date = Column(DateTime)
    first_author = Column(String(128))
    url = Column(String())
    source_type = Column(String(64))
    source_publisher = Column(String(256))
    summary = Column(String())
    study_name = Column(String())
    study_type = Column(String(128))
    country_id = Column(UUID(as_uuid=True))
    lead_organization = Column(String(128))
    sampling_start_date = Column(DateTime)
    sampling_end_date = Column(DateTime)
    age = Column(String(64))
    sex = Column(String(16))
    population_group = Column(String(128))
    sampling_method = Column(String(128))
    sensitivity = Column(Float)
    specificity = Column(Float)
    included = Column(Boolean)
    denominator_value = Column(Integer)
    numerator_definition = Column(String())
    serum_pos_prevalence = Column(Float)
    overall_risk_of_bias = Column(String(16))
    isotype_igg = Column(Boolean)
    isotype_igm = Column(Boolean)
    isotype_iga = Column(Boolean)
    specimen_type = Column(String(64))
    estimate_grade = Column(String(32))
    academic_primary_estimate = Column(Boolean)
    dashboard_primary_estimate = Column(Boolean)
    isotype_comb = Column(String(32))
    test_type = Column(String(256))
    test_adj = Column(Boolean)
    pop_adj = Column(Boolean)
    created_at = Column(DateTime)


# Research table for all additional research fields
class ResearchSource(db.Model):
    __tablename__ = 'research_source'

    source_id = Column(UUID(as_uuid=True), primary_key=True)
    case_population = Column(Integer)
    deaths_population = Column(Integer)
    age_max = Column(Float)
    age_min = Column(Float)
    age_variation = Column(String(128))
    age_variation_measure = Column(String(64))
    average_age = Column(String(256))
    case_count_neg14 = Column(Integer)
    case_count_neg9 = Column(Integer)
    case_count_0 = Column(Integer)
    death_count_plus11 = Column(Integer)
    death_count_plus4 = Column(Integer)
    ind_eval_lab = Column(String(128))
    ind_eval_link = Column(String())
    ind_se = Column(Float)
    ind_se_n = Column(Float)
    ind_sp = Column(Float)
    ind_sp_n = Column(Float)
    jbi_1 = Column(String(16))
    jbi_2 = Column(String(16))
    jbi_3 = Column(String(16))
    jbi_4 = Column(String(16))
    jbi_5 = Column(String(16))
    jbi_6 = Column(String(16))
    jbi_7 = Column(String(16))
    jbi_8 = Column(String(16))
    jbi_9 = Column(String(16))
    measure_of_age = Column(String(64))
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
    subgroup_var = Column(String(128))
    subgroup_cat = Column(String(128))
    superceded = Column(Boolean)
    test_linked_uid = Column(String())
    test_name = Column(String())
    test_validation = Column(String(128))
    created_at = Column(DateTime)


# Create base multi select tables
class Country(db.Model):
    __tablename__ = 'country'

    country_id = Column(UUID(as_uuid=True), primary_key=True)
    country_name = Column(String(128))
    country_iso3 = Column(String(4))
    latitude = Column(Float)
    longitude = Column(Float)
    created_at = Column(DateTime)


class City(db.Model):
    __tablename__ = 'city'

    city_id = Column(UUID(as_uuid=True), primary_key=True)
    city_name = Column(String(128))
    latitude = Column(Float)
    longitude = Column(Float)
    created_at = Column(DateTime)


class State(db.Model):
    __tablename__ = 'state'

    state_id = Column(UUID(as_uuid=True), primary_key=True)
    state_name = Column(String(128))
    latitude = Column(Float)
    longitude = Column(Float)
    created_at = Column(DateTime)


class TestManufacturer(db.Model):
    __tablename__ = 'test_manufacturer'

    test_manufacturer_id = Column(UUID(as_uuid=True), primary_key=True)
    test_manufacturer_name = Column(String(128))
    created_at = Column(DateTime)


class AntibodyTarget(db.Model):
    __tablename__ = 'antibody_target'

    antibody_target_id = Column(UUID(as_uuid=True), primary_key=True)
    antibody_target_name = Column(String(128))
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
