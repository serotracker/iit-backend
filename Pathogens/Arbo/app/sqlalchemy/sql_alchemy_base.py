from sqlalchemy import (
    Integer,
    VARCHAR,
    Column,
    Date,
    Float
)
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Estimates(Base):
    __tablename__ = 'estimates'

    estimate_id = Column(VARCHAR(length=255), unique=True, nullable=False, primary_key=True)
    sex = Column(VARCHAR(length=255))
    age = Column(VARCHAR(length=255))
    antibody = Column(VARCHAR(length=255))
    antigen = Column(VARCHAR(length=255))
    sample_size = Column(Integer)
    sample_numerator = Column(Integer)
    source_sheet = Column(VARCHAR(length=255))
    inclusion_criteria = Column(VARCHAR(length=255))
    pathogen = Column(VARCHAR(length=255))
    seroprevalence = Column(VARCHAR(length=255))
    longitude = Column(Float)
    latitude = Column(Float)
    sample_start_date = Column(Date)
    sample_end_date = Column(Date)
    assay = Column(VARCHAR(length=255))
    country = Column(VARCHAR(length=255))
    city = Column(VARCHAR(length=255))
    url = Column(VARCHAR(length=255))


Base.registry.configure()
