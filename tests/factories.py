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


