from sqlalchemy import Column, Integer, String, Float, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Таблица связи между организациями и телефонами
organization_phones = Table(
    'organization_phones',
    Base.metadata,
    Column('organization_id', Integer, ForeignKey('organizations.id')),
    Column('phone_id', Integer, ForeignKey('phones.id'))
)

# Таблица связи между организациями и видами деятельности
organization_activity = Table(
    'organization_activity',
    Base.metadata,
    Column('organization_id', Integer, ForeignKey('organizations.id')),
    Column('activity_id', Integer, ForeignKey('activities.id'))
)

class Phone(Base):
    __tablename__ = 'phones'
    
    id = Column(Integer, primary_key=True, index=True)
    number = Column(String, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"))

    organization = relationship('Organization', back_populates='phones')

class Activity(Base):
    __tablename__ = 'activities'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    parent_id = Column(Integer, ForeignKey('activities.id'), nullable=True)
    level = Column(Integer, default=1)  # Уровень вложенности

    # Отношения
    parent = relationship("Activity", remote_side=[id], backref="children")
    organizations = relationship('Organization', secondary=organization_activity, back_populates='activities')

class Building(Base):
    __tablename__ = 'buildings'
    
    id = Column(Integer, primary_key=True, index=True)
    address = Column(String, index=True)
    latitude = Column(Float)
    longitude = Column(Float)
    
    organizations = relationship('Organization', back_populates='building')

class Organization(Base):
    __tablename__ = 'organizations'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    building_id = Column(Integer, ForeignKey('buildings.id'))
    
    building = relationship('Building', back_populates='organizations')
    phones = relationship('Phone', back_populates='organization')
    activities = relationship('Activity', secondary=organization_activity, back_populates='organizations') 