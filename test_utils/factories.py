import uuid
from datetime import datetime
from random import random, randint
from app import db

import factory

from app.serotracker_sqlalchemy.models import DashboardSource, ResearchSource, AntibodyTarget, AntibodyTargetBridge,\
    City, CityBridge, Country, State, StateBridge, TestManufacturer, TestManufacturerBridge


# Note: Using this pattern instead of the previous function based pattern
# because we need to use the same class throughout our test fixture so that
# "sequence functions" work properly
class DashboardSourceFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = DashboardSource
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = 'commit'

    source_id = factory.LazyFunction(uuid.uuid4)
    source_name = factory.Sequence(lambda n: 'source_name_%d' % n)
    publication_date = factory.LazyFunction(datetime.now)
    first_author = factory.Sequence(lambda n: 'first_author_%d' % n)
    url = factory.Sequence(lambda n: 'https://source_url_%d.com' % n)
    source_type = factory.Sequence(lambda n: 'source_type_%d' % n)
    source_publisher = factory.Sequence(lambda n: 'source_publisher_%d' % n)
    summary = factory.Sequence(lambda n: 'summary_%d' % n)
    study_name = factory.Sequence(lambda n: 'study_name_%d' % n)
    study_type = factory.Sequence(lambda n: 'study_type_%d' % n)
    country_id = factory.LazyFunction(uuid.uuid4)
    lead_organization = factory.Sequence(lambda n: 'lead_organization_%d' % n)
    sampling_start_date = factory.LazyFunction(datetime.now)
    sampling_end_date = factory.LazyFunction(datetime.now)
    age = factory.Sequence(lambda n: 'age_%d' % n)
    sex = factory.Sequence(lambda n: 'sex_%d' % n)
    population_group = factory.Sequence(lambda n: 'population_group_%d' % n)
    sampling_method = factory.Sequence(lambda n: 'sampling_method_%d' % n)
    sensitivity = factory.LazyFunction(random)
    specificity = factory.LazyFunction(random)
    # Note: we use lambdas like this here because LazyFunction accepts a function as an arg rather than a val
    included = factory.LazyFunction(lambda: bool(randint(0, 1)))
    denominator_value = factory.LazyFunction(lambda: randint(100, 1000))
    numerator_definition = factory.Sequence(lambda n: 'numerator_definition_%d' % n)
    serum_pos_prevalence = factory.LazyFunction(random)
    overall_risk_of_bias = factory.Sequence(lambda n: 'bias_%d' % n)
    isotype_igg = factory.LazyFunction(lambda: bool(randint(0, 1)))
    isotype_igm = factory.LazyFunction(lambda: bool(randint(0, 1)))
    isotype_iga = factory.LazyFunction(lambda: bool(randint(0, 1)))
    specimen_type = factory.Sequence(lambda n: 'specimen_type_%d' % n)
    estimate_grade = factory.Sequence(lambda n: 'estimate_grade_%d' % n)
    academic_primary_estimate = factory.LazyFunction(lambda: bool(randint(0, 1)))
    # Make this true by default so that estimate prioritization always selects one record per study if no filters given
    dashboard_primary_estimate = True
    isotype_comb = factory.Sequence(lambda n: 'isotype_comb_%d' % n)
    test_type = factory.Sequence(lambda n: 'test_type_%d' % n)
    test_adj = factory.LazyFunction(lambda: bool(randint(0, 1)))
    pop_adj = factory.LazyFunction(lambda: bool(randint(0, 1)))
    created_at = factory.LazyFunction(datetime.now)
    cases_per_hundred = factory.LazyFunction(random)
    tests_per_hundred = factory.LazyFunction(random)
    deaths_per_hundred = factory.LazyFunction(random)
    vaccinations_per_hundred = factory.LazyFunction(random)
    full_vaccinations_per_hundred = factory.LazyFunction(random)
    vaccination_policy = factory.Sequence(lambda n: 'vaccination_policy_%d' % n)
    geo_exact_match = factory.LazyFunction(lambda: bool(randint(0, 1)))
    adj_prevalence = factory.LazyFunction(random)
    adj_prev_ci_lower = factory.LazyFunction(random)
    adj_prev_ci_upper = factory.LazyFunction(random)
    pin_latitude = factory.LazyFunction(random)
    pin_longitude = factory.LazyFunction(random)
    # Make this false by default so that no records are filtered out
    in_disputed_area = False
    subgroup_var = factory.Sequence(lambda n: 'subgroup_var_%d' % n)


class AntibodyTargetFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = AntibodyTarget
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = 'commit'
    antibody_target_id = factory.LazyFunction(uuid.uuid4)
    antibody_target_name = factory.Sequence(lambda n: 'antibody_target_name_%d' % n)
    created_at = factory.LazyFunction(datetime.now)


class AntibodyTargetBridgeFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = AntibodyTargetBridge
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = 'commit'
    id = factory.LazyFunction(uuid.uuid4)
    source_id = factory.LazyFunction(uuid.uuid4)
    antibody_target_id = factory.LazyFunction(uuid.uuid4)
    created_at = factory.LazyFunction(datetime.now)


class CityFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = City
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = 'commit'
    city_id = factory.LazyFunction(uuid.uuid4)
    city_name = factory.Sequence(lambda n: 'city_name_%d' % n)
    state_name = factory.Sequence(lambda n: 'city_state_name_%d' % n)
    latitude = factory.LazyFunction(random)
    longitude = factory.LazyFunction(random)
    created_at = factory.LazyFunction(datetime.now)


class CityBridgeFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = CityBridge
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = 'commit'
    id = factory.LazyFunction(uuid.uuid4)
    source_id = factory.LazyFunction(uuid.uuid4)
    city_id = factory.LazyFunction(uuid.uuid4)
    created_at = factory.LazyFunction(datetime.now)


class CountryFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Country
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = 'commit'
    country_id = factory.LazyFunction(uuid.uuid4)
    country_name = factory.Sequence(lambda n: 'country_name_%d' % n)
    country_iso3 = factory.Sequence(lambda n: '%d' % n)
    latitude = factory.LazyFunction(random)
    longitude = factory.LazyFunction(random)
    hrp_class = factory.Sequence(lambda n: 'hrp_class_%d' % n)
    income_class = factory.Sequence(lambda n: 'income_class_%d' % n)
    created_at = factory.LazyFunction(datetime.now)


class StateFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = State
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = 'commit'
    state_id = factory.LazyFunction(uuid.uuid4)
    state_name = factory.Sequence(lambda n: 'state_name_%d' % n)
    latitude = factory.LazyFunction(random)
    longitude = factory.LazyFunction(random)
    created_at = factory.LazyFunction(datetime.now)


class StateBridgeFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = StateBridge
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = 'commit'
    id = factory.LazyFunction(uuid.uuid4)
    source_id = factory.LazyFunction(uuid.uuid4)
    state_id = factory.LazyFunction(uuid.uuid4)
    created_at = factory.LazyFunction(datetime.now)


class TestManufacturerFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = TestManufacturer
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = 'commit'
    test_manufacturer_id = factory.LazyFunction(uuid.uuid4)
    test_manufacturer_name = factory.Sequence(lambda n: 'test_manufacturer_name_%d' % n)
    created_at = factory.LazyFunction(datetime.now)


class TestManufacturerBridgeFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = TestManufacturerBridge
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = 'commit'
    id = factory.LazyFunction(uuid.uuid4)
    source_id = factory.LazyFunction(uuid.uuid4)
    test_manufacturer_id = factory.LazyFunction(uuid.uuid4)
    created_at = factory.LazyFunction(datetime.now)


class ResearchSourceFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = ResearchSource
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = 'commit'
    source_id = factory.LazyFunction(uuid.uuid4)
    case_population = factory.LazyFunction(lambda: randint(1000, 100000))
    deaths_population = factory.LazyFunction(lambda: randint(1000, 100000))
    age_max = factory.LazyFunction(random)
    age_min = factory.LazyFunction(random)
    age_variation = factory.Sequence(lambda n: 'research_field_%d' % n)
    age_variation_measure = factory.Sequence(lambda n: 'research_field_%d' % n)
    average_age = factory.Sequence(lambda n: 'research_field_%d' % n)
    case_count_neg14 = factory.LazyFunction(lambda: randint(100, 1000))
    case_count_neg9 = factory.LazyFunction(lambda: randint(100, 1000))
    case_count_0 = factory.LazyFunction(lambda: randint(100, 1000))
    date_created = factory.LazyFunction(datetime.now)
    death_count_plus11 = factory.LazyFunction(lambda: randint(100, 1000))
    death_count_plus4 = factory.LazyFunction(lambda: randint(100, 1000))
    include_in_srma = factory.LazyFunction(lambda: bool(randint(0, 1)))
    sensspec_from_manufacturer = factory.LazyFunction(lambda: bool(randint(0, 1)))
    ind_se_n = factory.LazyFunction(random)
    ind_sp = factory.LazyFunction(random)
    ind_sp_n = factory.LazyFunction(random)
    jbi_1 = factory.Sequence(lambda n: 'research_field_%d' % n)
    jbi_2 = factory.Sequence(lambda n: 'research_field_%d' % n)
    jbi_3 = factory.Sequence(lambda n: 'research_field_%d' % n)
    jbi_4 = factory.Sequence(lambda n: 'research_field_%d' % n)
    jbi_5 = factory.Sequence(lambda n: 'research_field_%d' % n)
    jbi_6 = factory.Sequence(lambda n: 'research_field_%d' % n)
    jbi_7 = factory.Sequence(lambda n: 'research_field_%d' % n)
    jbi_8 = factory.Sequence(lambda n: 'research_field_%d' % n)
    jbi_9 = factory.Sequence(lambda n: 'research_field_%d' % n)
    last_modified_time = factory.LazyFunction(datetime.now)
    measure_of_age = factory.Sequence(lambda n: 'research_field_%d' % n)
    sample_frame_info = factory.Sequence(lambda n: 'research_field_%d' % n)
    number_of_females = factory.LazyFunction(lambda: randint(100, 1000))
    number_of_males = factory.LazyFunction(lambda: randint(100, 1000))
    numerator_value = factory.LazyFunction(random)
    estimate_name = factory.Sequence(lambda n: 'research_field_%d' % n)
    test_not_linked_reason = factory.Sequence(lambda n: 'research_field_%d' % n)
    se_n = factory.LazyFunction(random)
    seroprev_95_ci_lower = factory.LazyFunction(random)
    seroprev_95_ci_upper = factory.LazyFunction(random)
    sp_n = factory.LazyFunction(random)
    subgroup_cat = factory.Sequence(lambda n: 'research_field_%d' % n)
    subgroup_specific_category = factory.Sequence(lambda n: 'research_field_%d' % n)
    test_linked_uid = factory.Sequence(lambda n: 'research_field_%d' % n)
    test_name = factory.Sequence(lambda n: 'research_field_%d' % n)
    test_validation = factory.Sequence(lambda n: 'research_field_%d' % n)
    gbd_region = factory.Sequence(lambda n: 'research_field_%d' % n)
    gbd_subregion = factory.Sequence(lambda n: 'research_field_%d' % n)
    who_region = factory.Sequence(lambda n: 'research_field_%d' % n)
    lmic_hic = factory.Sequence(lambda n: 'research_field_%d' % n)
    genpop = factory.Sequence(lambda n: 'research_field_%d' % n)
    sampling_type = factory.Sequence(lambda n: 'research_field_%d' % n)
    airtable_record_id = factory.Sequence(lambda n: 'research_field_%d' % n)
    adj_sensitivity = factory.LazyFunction(random)
    adj_specificity = factory.LazyFunction(random)
    ind_eval_type = factory.Sequence(lambda n: 'research_field_%d' % n)
    created_at = factory.LazyFunction(datetime.now)
    zotero_citation_key = factory.Sequence(lambda n: 'research_field_%d' % n)
