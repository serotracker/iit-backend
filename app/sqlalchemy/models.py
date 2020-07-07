from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID

Base = declarative_base()


# Create airtable source table
class AirtableSource(Base):
    __tablename__ = 'airtable_source'

    source_id = Column(UUID, primary_key=True)
    source_name = Column(String(128))
    publication_date = Column(DateTime)
    first_author = Column(String)
    url = Column(String)
    source_type = Column(String)
    source_publisher = Column(String)
    summary = Column(String)
    study_type = Column(String)
    study_status = Column(String)
    country = Column(String)
    lead_organization = Column(String)
    sampling_start_date = Column(DateTime)
    sampling_end_date = Column(DateTime)
    sex = Column(String)
    sampling_method = Column(String)
    sensitivity = Column(Float)
    specificity = Column(Float)
    include_in_n = Column(String)
    denominator_value = Column(Integer)
    numerator_value = Column(Integer)
    numerator_definition = Column(String)
    serum_pos_prevalence = Column(Float)
    overall_risk_of_bias = Column(String)
    isotype_igg = Column(Boolean)
    isotype_igm = Column(Boolean)
    isotype_iga = Column(Boolean)
    created_at = Column(DateTime)


# Create base multi select tables
class City(Base):
    __tablename__ = 'city'

    city_id = Column(UUID, primary_key=True)
    city_name = Column(String)
    created_at = Column(DateTime)


class State(Base):
    __tablename__ = 'state'

    state_id = Column(UUID, primary_key=True)
    state_name = Column(String)
    created_at = Column(DateTime)


class Age(Base):
    __tablename__ = 'age'

    age_id = Column(UUID, primary_key=True)
    age_name = Column(String)
    created_at = Column(DateTime)


class PopulationGroup(Base):
    __tablename__ = 'population_group'

    population_group_id = Column(UUID, primary_key=True)
    population_group_name = Column(String)
    created_at = Column(DateTime)


class TestManufacturer(Base):
    __tablename__ = 'test_manufacturer'

    test_manufacturer_id = Column(UUID, primary_key=True)
    test_manufacturer_name = Column(String)
    created_at = Column(DateTime)


class ApprovingRegulator(Base):
    __tablename__ = 'approving_regulator'

    approving_regulator_id = Column(UUID, primary_key=True)
    approving_regulator_name = Column(String)
    created_at = Column(DateTime)


class TestType(Base):
    __tablename__ = 'test_type'

    test_type_id = Column(UUID, primary_key=True)
    test_type_name = Column(String)
    created_at = Column(DateTime)


class SpecimenType(Base):
    __tablename__ = 'specimen_type'

    specimen_type_id = Column(UUID, primary_key=True)
    specimen_type_name = Column(String)
    created_at = Column(DateTime)


# Create bridge tables
class CityBridge(Base):
    __tablename__ = 'city_bridge'

    id = Column(UUID, primary_key=True)
    source_id = Column(UUID)
    city_id = Column(UUID)
    created_at = Column(DateTime)


class StateBridge(Base):
    __tablename__ = 'state_bridge'

    id = Column(UUID, primary_key=True)
    source_id = Column(UUID)
    state_id = Column(UUID)
    created_at = Column(DateTime)


class AgeBridge(Base):
    __tablename__ = 'age_bridge'

    id = Column(UUID, primary_key=True)
    source_id = Column(UUID)
    age_id = Column(UUID)
    created_at = Column(DateTime)


class PopulationGroupBridge(Base):
    __tablename__ = 'population_group_bridge'

    id = Column(UUID, primary_key=True)
    source_id = Column(UUID)
    population_group_id = Column(UUID)
    created_at = Column(DateTime)


class TestManufacturerBridge(Base):
    __tablename__ = 'test_manufacturer_bridge'

    id = Column(UUID, primary_key=True)
    source_id = Column(UUID)
    test_manufacturer_id = Column(UUID)
    created_at = Column(DateTime)


class ApprovingRegulatorBridge(Base):
    __tablename__ = 'approving_regulator_bridge'

    id = Column(UUID, primary_key=True)
    source_id = Column(UUID)
    approving_regulator_id = Column(UUID)
    created_at = Column(DateTime)


class TestTypeBridge(Base):
    __tablename__ = 'test_type_bridge'

    id = Column(UUID, primary_key=True)
    source_id = Column(UUID)
    test_type_id = Column(UUID)
    created_at = Column(DateTime)


class SpecimenTypeBridge(Base):
    __tablename__ = 'specimen_type_bridge'

    id = Column(UUID, primary_key=True)
    source_id = Column(UUID)
    specimen_type_id = Column(UUID)
    created_at = Column(DateTime)
