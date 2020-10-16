from app import db
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID


# Create airtable source table
class AirtableSource(db.Model):
    __tablename__ = 'airtable_source'

    source_id = Column(UUID, primary_key=True)
    source_name = Column(String())
    publication_date = Column(DateTime)
    first_author = Column(String(128))
    url = Column(String())
    source_type = Column(String(64))
    source_publisher = Column(String(256))
    summary = Column(String())
    study_type = Column(String(128))
    study_status = Column(String(32))
    country = Column(String(64))
    lead_organization = Column(String(128))
    sampling_start_date = Column(DateTime)
    sampling_end_date = Column(DateTime)
    sex = Column(String(16))
    sampling_method = Column(String(128))
    sensitivity = Column(Float)
    specificity = Column(Float)
    include_in_n = Column(Boolean)
    denominator_value = Column(Integer)
    numerator_definition = Column(String())
    serum_pos_prevalence = Column(Float)
    overall_risk_of_bias = Column(String(16))
    isotype_igg = Column(Boolean)
    isotype_igm = Column(Boolean)
    isotype_iga = Column(Boolean)
    estimate_grade = Column(String(32))
    created_at = Column(DateTime)


# Create base multi select tables
class City(db.Model):
    __tablename__ = 'city'

    city_id = Column(UUID, primary_key=True)
    city_name = Column(String(128))
    created_at = Column(DateTime)


class State(db.Model):
    __tablename__ = 'state'

    state_id = Column(UUID, primary_key=True)
    state_name = Column(String(128))
    created_at = Column(DateTime)


class Age(db.Model):
    __tablename__ = 'age'

    age_id = Column(UUID, primary_key=True)
    age_name = Column(String(64))
    created_at = Column(DateTime)


class PopulationGroup(db.Model):
    __tablename__ = 'population_group'

    population_group_id = Column(UUID, primary_key=True)
    population_group_name = Column(String(128))
    created_at = Column(DateTime)


class TestManufacturer(db.Model):
    __tablename__ = 'test_manufacturer'

    test_manufacturer_id = Column(UUID, primary_key=True)
    test_manufacturer_name = Column(String(128))
    created_at = Column(DateTime)


class ApprovingRegulator(db.Model):
    __tablename__ = 'approving_regulator'

    approving_regulator_id = Column(UUID, primary_key=True)
    approving_regulator_name = Column(String(256))
    created_at = Column(DateTime)


class TestType(db.Model):
    __tablename__ = 'test_type'

    test_type_id = Column(UUID, primary_key=True)
    test_type_name = Column(String(256))
    created_at = Column(DateTime)


class SpecimenType(db.Model):
    __tablename__ = 'specimen_type'

    specimen_type_id = Column(UUID, primary_key=True)
    specimen_type_name = Column(String(64))
    created_at = Column(DateTime)


# Create bridge tables
class CityBridge(db.Model):
    __tablename__ = 'city_bridge'

    id = Column(UUID, primary_key=True)
    source_id = Column(UUID)
    city_id = Column(UUID)
    created_at = Column(DateTime)


class StateBridge(db.Model):
    __tablename__ = 'state_bridge'

    id = Column(UUID, primary_key=True)
    source_id = Column(UUID)
    state_id = Column(UUID)
    created_at = Column(DateTime)


class AgeBridge(db.Model):
    __tablename__ = 'age_bridge'

    id = Column(UUID, primary_key=True)
    source_id = Column(UUID)
    age_id = Column(UUID)
    created_at = Column(DateTime)


class PopulationGroupBridge(db.Model):
    __tablename__ = 'population_group_bridge'

    id = Column(UUID, primary_key=True)
    source_id = Column(UUID)
    population_group_id = Column(UUID)
    created_at = Column(DateTime)


class TestManufacturerBridge(db.Model):
    __tablename__ = 'test_manufacturer_bridge'

    id = Column(UUID, primary_key=True)
    source_id = Column(UUID)
    test_manufacturer_id = Column(UUID)
    created_at = Column(DateTime)


class ApprovingRegulatorBridge(db.Model):
    __tablename__ = 'approving_regulator_bridge'

    id = Column(UUID, primary_key=True)
    source_id = Column(UUID)
    approving_regulator_id = Column(UUID)
    created_at = Column(DateTime)


class TestTypeBridge(db.Model):
    __tablename__ = 'test_type_bridge'

    id = Column(UUID, primary_key=True)
    source_id = Column(UUID)
    test_type_id = Column(UUID)
    created_at = Column(DateTime)


class SpecimenTypeBridge(db.Model):
    __tablename__ = 'specimen_type_bridge'

    id = Column(UUID, primary_key=True)
    source_id = Column(UUID)
    specimen_type_id = Column(UUID)
    created_at = Column(DateTime)
