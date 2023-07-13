from sqlalchemy import (
    Integer,
    VARCHAR,
    Column,
    Date,
    Float,
    ForeignKey,
    MetaData,
    DateTime,
    Text,
    func
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
    __table_args__ = {"schema": "arbo"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True)
    antibody = Column(VARCHAR(length=255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class AntibodyToEstimate(Base):
    __tablename__ = 'antibody_to_estimate'
    __table_args__ = {"schema": "arbo"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True)
    antibody_id = Column(ForeignKey("antibody.id"), index=True)
    antibody = relationship("Antibody", foreign_keys="AntibodyToEstimate.antibody_id")
    estimate_id = Column(ForeignKey("estimate.id"), index=True)
    estimate = relationship("Estimate", foreign_keys="AntibodyToEstimate.estimate_id")
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Antigen(Base):
    __tablename__ = 'antigen'
    __table_args__ = {"schema": "arbo"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True)
    antigen = Column(VARCHAR(length=255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class AntigenToEstimate(Base):
    __tablename__ = 'antigen_to_estimate'
    __table_args__ = {"schema": "arbo"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True)
    antigen_id = Column(ForeignKey("antigen.id"), index=True)
    antigen = relationship("Antigen", foreign_keys="AntigenToEstimate.antigen_id")
    estimate_id = Column(ForeignKey("estimate.id"), index=True)
    estimate = relationship("Estimate", foreign_keys="AntigenToEstimate.estimate_id")
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class SourceSheet(Base):
    __tablename__ = 'source_sheet'
    __table_args__ = {"schema": "arbo"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True)
    source_title = Column(Text)
    extractor = Column(VARCHAR(length=255))
    first_author = Column(VARCHAR(length=255))
    publication_date = Column(Date)
    url = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Estimate(Base):
    __tablename__ = 'estimate'
    __table_args__ = {"schema": "arbo"}

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
    inclusion_criteria = Column(Text)

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
    url = Column(Text)
    source_sheet_id = Column(UUID(as_uuid=True), ForeignKey('source_sheet.id'))
    source_sheet = relationship("SourceSheet", backref="estimate")
    created_at = Column(DateTime(timezone=True), server_default=func.now())


Base.registry.configure()
