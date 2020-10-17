import uuid
from datetime import datetime
from random import random, randint, getrandbits

import factory

from app.serotracker_sqlalchemy.models import AirtableSource, Age, AgeBridge, ApprovingRegulator, \
    ApprovingRegulatorBridge, City, CityBridge, PopulationGroup, PopulationGroupBridge, State, StateBridge, \
    SpecimenType, SpecimenTypeBridge, TestType, TestTypeBridge, TestManufacturer, TestManufacturerBridge


def airtable_source_factory(_session, **kwargs):
    class AirtableSourceFactory(factory.alchemy.SQLAlchemyModelFactory):
        class Meta:
            model = AirtableSource
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
        study_type = factory.Sequence(lambda n: 'study_type_%d' % n)
        study_status = factory.Sequence(lambda n: 'study_status_%d' % n)
        country = factory.Sequence(lambda n: 'country_%d' % n)
        lead_organization = factory.Sequence(lambda n: 'lead_organization_%d' % n)
        sampling_start_date = factory.LazyFunction(datetime.now)
        sampling_end_date = factory.LazyFunction(datetime.now)
        sex = factory.Sequence(lambda n: 'sex_%d' % n)
        sampling_method = factory.Sequence(lambda n: 'sampling_method_%d' % n)
        sensitivity = random()
        specificity = random()
        include_in_n = bool(randint(0, 1))
        denominator_value = randint(100, 1000)
        numerator_definition = factory.Sequence(lambda n: 'numerator_definition_%d' % n)
        serum_pos_prevalence = random()
        overall_risk_of_bias = factory.Sequence(lambda n: 'bias_%d' % n)
        isotype_igg = bool(randint(0, 1))
        isotype_igm = bool(randint(0, 1))
        isotype_iga = bool(randint(0, 1))
        estimate_grade = factory.Sequence(lambda n: 'estimate_grade_%d' % n)
        created_at = factory.LazyFunction(datetime.now)
    return AirtableSourceFactory(**kwargs)


def age_factory(_session, **kwargs):
    class AgeFactory(factory.alchemy.SQLAlchemyModelFactory):
        class Meta:
            model = Age
            sqlalchemy_session = _session
            sqlalchemy_session_persistence = 'commit'
        age_id = uuid.uuid4()
        age_name = factory.Sequence(lambda n: 'age_name_%d' % n)
        created_at = factory.LazyFunction(datetime.now)
    return AgeFactory(**kwargs)


def age_bridge_factory(_session, **kwargs):
    class AgeBridgeFactory(factory.alchemy.SQLAlchemyModelFactory):
        class Meta:
            model = AgeBridge
            sqlalchemy_session = _session
            sqlalchemy_session_persistence = 'commit'
        id = uuid.uuid4()
        source_id = uuid.uuid4()
        age_id = uuid.uuid4()
        created_at = factory.LazyFunction(datetime.now)
    return AgeBridgeFactory(**kwargs)


def approving_regulator_factory(_session, **kwargs):
    class ApprovingRegulatorFactory(factory.alchemy.SQLAlchemyModelFactory):
        class Meta:
            model = ApprovingRegulator
            sqlalchemy_session = _session
            sqlalchemy_session_persistence = 'commit'
        approving_regulator_id = uuid.uuid4()
        approving_regulator_name = factory.Sequence(lambda n: 'approving_regulator_name_%d' % n)
        created_at = factory.LazyFunction(datetime.now)
    return ApprovingRegulatorFactory(**kwargs)


def approving_regulator_bridge_factory(_session, **kwargs):
    class ApprovingRegulatorBridgeFactory(factory.alchemy.SQLAlchemyModelFactory):
        class Meta:
            model = ApprovingRegulatorBridge
            sqlalchemy_session = _session
            sqlalchemy_session_persistence = 'commit'
        id = uuid.uuid4()
        source_id = uuid.uuid4()
        approving_regulator_id = uuid.uuid4()
        created_at = factory.LazyFunction(datetime.now)
    return ApprovingRegulatorBridgeFactory(**kwargs)


def city_factory(_session, **kwargs):
    class CityFactory(factory.alchemy.SQLAlchemyModelFactory):
        class Meta:
            model = City
            sqlalchemy_session = _session
            sqlalchemy_session_persistence = 'commit'
        city_id = uuid.uuid4()
        city_name = factory.Sequence(lambda n: 'city_name_%d' % n)
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


def population_group_factory(_session, **kwargs):
    class PopulationGroupFactory(factory.alchemy.SQLAlchemyModelFactory):
        class Meta:
            model = PopulationGroup
            sqlalchemy_session = _session
            sqlalchemy_session_persistence = 'commit'
        population_group_id = uuid.uuid4()
        population_group_name = factory.Sequence(lambda n: 'population_group_name_%d' % n)
        created_at = factory.LazyFunction(datetime.now)
    return PopulationGroupFactory(**kwargs)


def population_group_bridge_factory(_session, **kwargs):
    class PopulationGroupBridgeFactory(factory.alchemy.SQLAlchemyModelFactory):
        class Meta:
            model = PopulationGroupBridge
            sqlalchemy_session = _session
            sqlalchemy_session_persistence = 'commit'
        id = uuid.uuid4()
        source_id = uuid.uuid4()
        population_group_id = uuid.uuid4()
        created_at = factory.LazyFunction(datetime.now)
    return PopulationGroupBridgeFactory(**kwargs)


def state_factory(_session, **kwargs):
    class StateFactory(factory.alchemy.SQLAlchemyModelFactory):
        class Meta:
            model = State
            sqlalchemy_session = _session
            sqlalchemy_session_persistence = 'commit'
        state_id = uuid.uuid4()
        state_name = factory.Sequence(lambda n: 'state_name_%d' % n)
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


def specimen_type_factory(_session, **kwargs):
    class SpecimenTypeFactory(factory.alchemy.SQLAlchemyModelFactory):
        class Meta:
            model = SpecimenType
            sqlalchemy_session = _session
            sqlalchemy_session_persistence = 'commit'
        specimen_type_id = uuid.uuid4()
        specimen_type_name = factory.Sequence(lambda n: 'specimen_type_name_%d' % n)
        created_at = factory.LazyFunction(datetime.now)
    return SpecimenTypeFactory(**kwargs)


def specimen_type_bridge_factory(_session, **kwargs):
    class SpecimenTypeBridgeFactory(factory.alchemy.SQLAlchemyModelFactory):
        class Meta:
            model = SpecimenTypeBridge
            sqlalchemy_session = _session
            sqlalchemy_session_persistence = 'commit'
        id = uuid.uuid4()
        source_id = uuid.uuid4()
        specimen_type_id = uuid.uuid4()
        created_at = factory.LazyFunction(datetime.now)
    return SpecimenTypeBridgeFactory(**kwargs)


def test_type_factory(_session, **kwargs):
    class TestTypeFactory(factory.alchemy.SQLAlchemyModelFactory):
        class Meta:
            model = TestType
            sqlalchemy_session = _session
            sqlalchemy_session_persistence = 'commit'
        test_type_id = uuid.uuid4()
        test_type_name = factory.Sequence(lambda n: 'test_type_name_%d' % n)
        created_at = factory.LazyFunction(datetime.now)
    return TestTypeFactory(**kwargs)


def test_type_bridge_factory(_session, **kwargs):
    class TestTypeBridgeFactory(factory.alchemy.SQLAlchemyModelFactory):
        class Meta:
            model = TestTypeBridge
            sqlalchemy_session = _session
            sqlalchemy_session_persistence = 'commit'
        id = uuid.uuid4()
        source_id = uuid.uuid4()
        test_type_id = uuid.uuid4()
        created_at = factory.LazyFunction(datetime.now)
    return TestTypeBridgeFactory(**kwargs)


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
