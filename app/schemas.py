from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class PhoneBase(BaseModel):
    number: str

class PhoneCreate(PhoneBase):
    pass

class Phone(PhoneBase):
    id: int
    organization_id: int

    class Config:
        from_attributes = True

class ActivityBase(BaseModel):
    name: str
    parent_id: Optional[int] = None
    level: int = 1

class ActivityCreate(ActivityBase):
    pass

class Activity(ActivityBase):
    id: int
    children: List['Activity'] = []

    class Config:
        from_attributes = True

class BuildingBase(BaseModel):
    address: str
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)

class BuildingCreate(BuildingBase):
    pass

class Building(BuildingBase):
    id: int

    class Config:
        from_attributes = True

class OrganizationBase(BaseModel):
    name: str
    building_id: int

class OrganizationCreate(OrganizationBase):
    phones: List[str]
    activities: List[int]

class Organization(OrganizationBase):
    id: int
    building: Building
    phones: List[Phone]
    activities: List[Activity]

    class Config:
        from_attributes = True

# Схемы для поиска
class GeoPoint(BaseModel):
    latitude: float
    longitude: float

class GeoRectangle(BaseModel):
    north_west: GeoPoint
    south_east: GeoPoint

class GeoSearchParams(BaseModel):
    center: GeoPoint
    radius_km: Optional[float] = None
    rectangle: Optional[GeoRectangle] = None

class ActivitySearchParams(BaseModel):
    activity_name: str
    include_children: bool = True

class OrganizationSearchParams(BaseModel):
    name: str 