from sqlalchemy import (
    Integer,
    VARCHAR,
    Column,
    Date,
    Float,
    ForeignKey,
    MetaData
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import uuid

# If you want to create a new migration,
# simply change the model definitions in Pathogens/Arbo/app/sqlalchemy/sql_alchemy_base.py (here)
# and run the following command: alembic revision --autogenerate -m "<name of the migration>".
# This will autogenerate any new changes based on the updated models
# and then to apply the change, run alembic upgrade head again.
Base = declarative_base(metadata=MetaData(schema="arbo"))

class Antibody(Base):
    __tablename__ = 'antibody'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True)
    antibody = Column(VARCHAR(length=255))
    created_at = Column(Date)

class AntibodyToEstimate(Base):
    __tablename__ = 'antibody_to_estimate'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True)
    antibody_id = Column(UUID(as_uuid=True), ForeignKey("antibody.id"), index=True)
    antibody = relationship("Antibody", foreign_keys=[antibody_id])
    estimate_id = Column(UUID(as_uuid=True), ForeignKey("estimate.id"), index=True)
    estimate = relationship("Estimate", foreign_keys=[estimate_id])
    created_at = Column(Date)

class Antigen(Base):
    __tablename__ = 'antigen'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True)
    antigen = Column(VARCHAR(length=255))
    created_at = Column(Date)

class AntigenToEstimate(Base):
    __tablename__ = 'antigen_to_estimate'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True)
    antigen_id = Column(UUID(as_uuid=True), ForeignKey("antigen.id"), index=True)
    antigen = relationship("Antigen", foreign_keys=[antigen_id])
    estimate_id = Column(UUID(as_uuid=True), ForeignKey("estimate.id"), index=True)
    estimate = relationship("Estimate", foreign_keys=[estimate_id])
    created_at = Column(Date)

# class City(Base):
#     __tablename__ = 'city'
#
#     id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True)
#     city = Column(VARCHAR(length=255))
#     created_at = Column(Date)
#
# class CityBridge(Base):
#     __tablename__ = 'city_bridge'
#
#     id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True)
#     city_id = Column(ForeignKey("city.id"), index=True)
#     city = relationship("City", foreign_keys="CityBridge.city_id")
#     estimate_id = Column(ForeignKey("estimates.id"), index=True)
#     estimate = relationship("Estimates", foreign_keys="CityBridge.estimate_id")
#     created_at = Column(Date)
#
# class State(Base):
#     __tablename__ = 'state'
#
#     id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True)
#     state = Column(VARCHAR(length=255))
#     created_at = Column(Date)
#
# class StateBridge(Base):
#     __tablename__ = 'state_bridge'
#
#     id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True)
#     state_id = Column(ForeignKey("state.id"), index=True)
#     state = relationship("State", foreign_keys="StateBridge.state_id")
#     estimate_id = Column(ForeignKey("estimates.id"), index=True)
#     estimate = relationship("Estimates", foreign_keys="StateBridge.estimate_id")
#     created_at = Column(Date)
#
# class Country(Base):
#     __tablename__ = 'country'
#
#     id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True)
#     country = Column(VARCHAR(length=255))
#     created_at = Column(Date)
#
# class CountryBridge(Base):
#     __tablename__ = 'country_bridge'
#
#     id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True)
#     country_id = Column(ForeignKey("country.id"), index=True)
#     country = relationship("Country", foreign_keys="CountryBridge.country_id")
#     estimate_id = Column(ForeignKey("estimates.id"), index=True)
#     estimate = relationship("Estimates", foreign_keys="CountryBridge.estimate_id")
#     created_at = Column(Date)

class SourceSheet(Base):
    __tablename__ = 'source_sheet'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True)
    source_title = Column(VARCHAR(length=255))
    extractor = Column(VARCHAR(length=255))
    first_author = Column(VARCHAR(length=255))
    publication_date = Column(Date)
    url = Column(VARCHAR(length=255))
    created_at = Column(Date)

class Estimate(Base):
    __tablename__ = 'estimate'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True)
    sex = Column(VARCHAR(length=255))
    age_minimum = Column(Integer)
    age_maximum = Column(Integer)
    age_group = Column(VARCHAR(length=255))
    assay_other = Column(VARCHAR(length=255))
    producer = Column(VARCHAR(length=255))
    producer_other = Column(VARCHAR(length=255))
    sample_frame = Column(VARCHAR(length=255))
    same_frame_target_group = Column(VARCHAR(length=255))
    sample_size = Column(Integer)
    sample_numerator = Column(Integer)
    inclusion_criteria = Column(VARCHAR(length=2048))
    pathogen = Column(VARCHAR(length=255))
    seroprevalence = Column(VARCHAR(length=255))
    country = Column(VARCHAR(length=255))
    state = Column(VARCHAR(length=255))
    city = Column(VARCHAR(length=255))
    longitude = Column(Float)
    latitude = Column(Float)
    sample_start_date = Column(Date)
    sample_end_date = Column(Date)
    assay = Column(VARCHAR(length=255))
    url = Column(VARCHAR(length=512))
    source_sheet_id = Column(UUID(as_uuid=True), ForeignKey('source_sheet.id'))
    source_sheet = relationship("SourceSheet", backref="estimate")
    created_at = Column(Date)


Base.registry.configure()
