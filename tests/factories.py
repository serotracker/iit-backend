import uuid
from datetime import datetime
from random import random, randint

import factory

from app.serotracker_sqlalchemy.models import DashboardSource, ResearchSource, AntibodyTarget, AntibodyTargetBridge,\
    City, CityBridge, Country, State, StateBridge, TestManufacturer, TestManufacturerBridge


def dashboard_source_factory(_session, **kwargs):
    class DashboardSourceFactory(factory.alchemy.SQLAlchemyModelFactory):
        class Meta:
            model = DashboardSource
            sqlalchemy_session = _session
            sqlalchemy_session_persistence = 'commit'

        source_id = uuid.uuid4()
        source_name = factory.Sequence(lambda n: 'source_name_%d' % n)
        publication_date = factory.LazyFunction(datetime.now)
        first_author = factory.Sequence(lambda n: 'first_author_%d' % n)
        url = factory.Sequence(lambda n: 'https://source_url_%d.com' % n)
        source_type = factory.Sequence(lambda n: 'source_type_%d' % n)
        source_publisher = factory.Sequence(lambda n: 'source_publisher_%d' % n)
        summary = factory.Sequence(lambda n: 'summary_%d' % n)
        study_name = factory.Sequence(lambda n: 'study_name_%d' % n)
        study_type = factory.Sequence(lambda n: 'study_type_%d' % n)
        country_id = uuid.uuid4()
        lead_organization = factory.Sequence(lambda n: 'lead_organization_%d' % n)
        sampling_start_date = factory.LazyFunction(datetime.now)
        sampling_end_date = factory.LazyFunction(datetime.now)
        age = factory.Sequence(lambda n: 'age_%d' % n)
        sex = factory.Sequence(lambda n: 'sex_%d' % n)
        population_group = factory.Sequence(lambda n: 'population_group_%d' % n)
        sampling_method = factory.Sequence(lambda n: 'sampling_method_%d' % n)
        sensitivity = random()
        specificity = random()
        included = bool(randint(0, 1))
        denominator_value = randint(100, 1000)
        numerator_definition = factory.Sequence(lambda n: 'numerator_definition_%d' % n)
        serum_pos_prevalence = random()
        overall_risk_of_bias = factory.Sequence(lambda n: 'bias_%d' % n)
        isotype_igg = bool(randint(0, 1))
        isotype_igm = bool(randint(0, 1))
        isotype_iga = bool(randint(0, 1))
        specimen_type = factory.Sequence(lambda n: 'specimen_type_%d' % n)
        estimate_grade = factory.Sequence(lambda n: 'estimate_grade_%d' % n)
        academic_primary_estimate = bool(randint(0, 1))
        dashboard_primary_estimate = bool(randint(0, 1))
        isotype_comb = factory.Sequence(lambda n: 'isotype_comb_%d' % n)
        test_type = factory.Sequence(lambda n: 'test_type_%d' % n)
        test_adj = bool(randint(0, 1))
        pop_adj = bool(randint(0, 1))
        created_at = factory.LazyFunction(datetime.now)
        cases_per_hundred = random()
        tests_per_hundred = random()
        deaths_per_hundred = random()
        vaccinations_per_hundred = random()
        full_vaccinations_per_hundred = random()
        vaccination_policy = factory.Sequence(lambda n: 'vaccination_policy_%d' % n)
        geo_exact_match = bool(randint(0, 1))
        adj_prevalence = random()
        adj_prev_ci_lower = random()
        adj_prev_ci_upper = random()
        pin_latitude = random()
        pin_longitude = random()
        in_disputed_area = bool(randint(0, 1))
        subgroup_var = factory.Sequence(lambda n: 'subgroup_var_%d' % n)

    return DashboardSourceFactory(**kwargs)


def antibody_target_factory(_session, **kwargs):
    class AntibodyTargetFactory(factory.alchemy.SQLAlchemyModelFactory):
        class Meta:
            model = AntibodyTarget
            sqlalchemy_session = _session
            sqlalchemy_session_persistence = 'commit'
        antibody_target_id = uuid.uuid4()
        antibody_target_name = factory.Sequence(lambda n: 'city_name_%d' % n)
        created_at = factory.LazyFunction(datetime.now)
    return AntibodyTargetFactory(**kwargs)


def antibody_target_bridge_factory(_session, **kwargs):
    class AntibodyTargetBridgeFactory(factory.alchemy.SQLAlchemyModelFactory):
        class Meta:
            model = AntibodyTargetBridge
            sqlalchemy_session = _session
            sqlalchemy_session_persistence = 'commit'
        id = uuid.uuid4()
        source_id = uuid.uuid4()
        antibody_target_id = uuid.uuid4()
        created_at = factory.LazyFunction(datetime.now)
    return AntibodyTargetBridgeFactory(**kwargs)


def city_factory(_session, **kwargs):
    class CityFactory(factory.alchemy.SQLAlchemyModelFactory):
        class Meta:
            model = City
            sqlalchemy_session = _session
            sqlalchemy_session_persistence = 'commit'
        city_id = uuid.uuid4()
        city_name = factory.Sequence(lambda n: 'city_name_%d' % n)
        state_name = factory.Sequence(lambda n: 'state_name_%d' % n)
        latitude = random()
        longitude = random()
        created_at = factory.LazyFunction(datetime.now)
    return CityFactory(**kwargs)


def city_bridge_factory(_session, **kwargs):
    class CityBridgeFactory(factory.alchemy.SQLAlchemyModelFactory):
        class Meta:
            model = CityBridge
            sqlalchemy_session = _session
            sqlalchemy_session_persistence = 'commit'
        id = uuid.uuid4()
        source_id = uuid.uuid4()
        city_id = uuid.uuid4()
        created_at = factory.LazyFunction(datetime.now)
    return CityBridgeFactory(**kwargs)


def country_factory(_session, **kwargs):
    class CountryFactory(factory.alchemy.SQLAlchemyModelFactory):
        class Meta:
            model = Country
            sqlalchemy_session = _session
            sqlalchemy_session_persistence = 'commit'
        country_id = uuid.uuid4()
        country_name = factory.Sequence(lambda n: 'country_name_%d' % n)
        country_iso3 = factory.Sequence(lambda n: '%d' % n)
        latitude = random()
        longitude = random()
        hrp_class = factory.Sequence(lambda n: 'hrp_class_%d' % n)
        income_class = factory.Sequence(lambda n: 'income_class_%d' % n)
        created_at = factory.LazyFunction(datetime.now)
    return CountryFactory(**kwargs)


def state_factory(_session, **kwargs):
    class StateFactory(factory.alchemy.SQLAlchemyModelFactory):
        class Meta:
            model = State
            sqlalchemy_session = _session
            sqlalchemy_session_persistence = 'commit'
        state_id = uuid.uuid4()
        state_name = factory.Sequence(lambda n: 'state_name_%d' % n)
        latitude = random()
        longitude = random()
        created_at = factory.LazyFunction(datetime.now)
    return StateFactory(**kwargs)


def state_bridge_factory(_session, **kwargs):
    class StateBridgeFactory(factory.alchemy.SQLAlchemyModelFactory):
        class Meta:
            model = StateBridge
            sqlalchemy_session = _session
            sqlalchemy_session_persistence = 'commit'
        id = uuid.uuid4()
        source_id = uuid.uuid4()
        state_id = uuid.uuid4()
        created_at = factory.LazyFunction(datetime.now)
    return StateBridgeFactory(**kwargs)


def test_manufacturer_factory(_session, **kwargs):
    class TestManufacturerFactory(factory.alchemy.SQLAlchemyModelFactory):
        class Meta:
            model = TestManufacturer
            sqlalchemy_session = _session
            sqlalchemy_session_persistence = 'commit'
        test_manufacturer_id = uuid.uuid4()
        test_manufacturer_name = factory.Sequence(lambda n: 'test_manufacturer_name_%d' % n)
        created_at = factory.LazyFunction(datetime.now)
    return TestManufacturerFactory(**kwargs)


def test_manufacturer_bridge_factory(_session, **kwargs):
    class TestManufacturerBridgeFactory(factory.alchemy.SQLAlchemyModelFactory):
        class Meta:
            model = TestManufacturerBridge
            sqlalchemy_session = _session
            sqlalchemy_session_persistence = 'commit'
        id = uuid.uuid4()
        source_id = uuid.uuid4()
        test_manufacturer_id = uuid.uuid4()
        created_at = factory.LazyFunction(datetime.now)
    return TestManufacturerBridgeFactory(**kwargs)


# TODO: finish setting up this factory class
def research_source_factory(_session, **kwargs):
    class ResearchSourceFactory(factory.alchemy.SQLAlchemyModelFactory):
        class Meta:
            model = ResearchSource
            sqlalchemy_session = _session
            sqlalchemy_session_persistence = 'commit'
        source_id = uuid.uuid4()
        case_population = randint(1000, 10000000000000)
        deaths_population = randint(1000, 10000000000000)
        age_max = random()
        age_min = random()
        age_variation = factory.Sequence(lambda n: 'research_field_%d' % n)
        age_variation_measure = factory.Sequence(lambda n: 'research_field_%d' % n)
        average_age = factory.Sequence(lambda n: 'research_field_%d' % n)
        case_count_neg14 = randint(100, 1000)
        case_count_neg9 = randint(100, 1000)
        case_count_0 = randint(100, 1000)
        date_created = factory.LazyFunction(datetime.now)
        death_count_plus11 = randint(100, 1000)
        death_count_plus4 = randint(100, 1000)
        include_in_srma = bool(randint(0, 1))
        sensspec_from_manufacturer = bool(randint(0, 1))
        ind_eval_lab = factory.Sequence(lambda n: 'research_field_%d' % n)
        ind_eval_link = factory.Sequence(lambda n: 'research_field_%d' % n)
        ind_se = random()
        ind_se_n = random()
        ind_sp = random()
        ind_sp_n = random()
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
        number_of_females = randint(100, 1000)
        number_of_males = randint(100, 1000)
        numerator_value = random()
        estimate_name = factory.Sequence(lambda n: 'research_field_%d' % n)
        test_not_linked_reason = factory.Sequence(lambda n: 'research_field_%d' % n)
        se_n = random()
        seroprev_95_ci_lower = random()
        seroprev_95_ci_upper = random()
        sp_n = random()
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
        adj_sensitivity = random()
        adj_specificity = random()
        ind_eval_type = factory.Sequence(lambda n: 'research_field_%d' % n)
        created_at = factory.LazyFunction(datetime.now)
        zotero_citation_key = factory.Sequence(lambda n: 'research_field_%d' % n)
    return ResearchSourceFactory(**kwargs)
