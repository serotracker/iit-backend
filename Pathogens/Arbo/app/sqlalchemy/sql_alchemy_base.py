from sqlalchemy import (
    Integer,
    VARCHAR,
    Column,
    Date,
    Float,
    ForeignKey,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import uuid

Base = declarative_base()


class Antibody(Base):
    __tablename__ = 'antibody'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True)
    antibody = Column(VARCHAR(length=255))


class AntibodyBridge(Base):
    __tablename__ = 'antibody_bridge'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True)
    antibody_id = Column(ForeignKey("antibody.id"), index=True)
    antibody = relationship("Antibody", foreign_keys="AntibodyBridge.antibody_id")
    estimate_id = Column(ForeignKey("estimates.id"), index=True)
    estimate = relationship("Estimates", foreign_keys="AntibodyBridge.estimate_id")


class Antigen(Base):
    __tablename__ = 'antigen'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True)
    antigen = Column(VARCHAR(length=255))


class AntigenBridge(Base):
    __tablename__ = 'antigen_bridge'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True)
    antigen_id = Column(ForeignKey("antigen.id"), index=True)
    antigen = relationship("Antigen", foreign_keys="AntigenBridge.antigen_id")
    estimate_id = Column(ForeignKey("estimates.id"), index=True)
    estimate = relationship("Estimates", foreign_keys="AntigenBridge.estimate_id")


class City(Base):
    __tablename__ = 'city'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True)
    city = Column(VARCHAR(length=255))


class CityBridge(Base):
    __tablename__ = 'city_bridge'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True)
    city_id = Column(ForeignKey("city.id"), index=True)
    city = relationship("City", foreign_keys="CityBridge.city_id")
    estimate_id = Column(ForeignKey("estimates.id"), index=True)
    estimate = relationship("Estimates", foreign_keys="CityBridge.estimate_id")


class State(Base):
    __tablename__ = 'state'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True)
    state = Column(VARCHAR(length=255))


class StateBridge(Base):
    __tablename__ = 'state_bridge'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True)
    state_id = Column(ForeignKey("state.id"), index=True)
    state = relationship("State", foreign_keys="StateBridge.state_id")
    estimate_id = Column(ForeignKey("estimates.id"), index=True)
    estimate = relationship("Estimates", foreign_keys="StateBridge.estimate_id")


class Country(Base):
    __tablename__ = 'country'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True)
    country = Column(VARCHAR(length=255))


class CountryBridge(Base):
    __tablename__ = 'country_bridge'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True)
    country_id = Column(ForeignKey("country.id"), index=True)
    country = relationship("Country", foreign_keys="CountryBridge.country_id")
    estimate_id = Column(ForeignKey("estimates.id"), index=True)
    estimate = relationship("Estimates", foreign_keys="CountryBridge.estimate_id")


class SourceSheet(Base):
    __tablename__ = 'source_sheet'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True)
    source_title = Column(VARCHAR(length=255))
    extractor = Column(VARCHAR(length=255))
    first_author = Column(VARCHAR(length=255))
    publication_date = Column(Date)
    url = Column(VARCHAR(length=255))


class SourceSheetBridge(Base):
    __tablename__ = 'source_sheet_bridge'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True)
    source_sheet_id = Column(ForeignKey("source_sheet.id"), index=True)
    source_sheet = relationship("SourceSheet", foreign_keys="SourceSheetBridge.source_sheet_id")
    estimate_id = Column(ForeignKey("estimates.id"), index=True)
    estimate = relationship("Estimates", foreign_keys="SourceSheetBridge.estimate_id")


class Estimates(Base):
    __tablename__ = 'estimates'

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
    inclusion_criteria = Column(VARCHAR(length=255))
    pathogen = Column(VARCHAR(length=255))
    seroprevalence = Column(VARCHAR(length=255))
    longitude = Column(Float)
    latitude = Column(Float)
    sample_start_date = Column(Date)
    sample_end_date = Column(Date)
    assay = Column(VARCHAR(length=255))
    url = Column(VARCHAR(length=255))


Base.registry.configure()
