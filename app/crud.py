from sqlalchemy.orm import Session
from sqlalchemy import func
from . import models, schemas
from typing import List, Optional
import math

# CRUD для телефонов
def create_phone(db: Session, phone: schemas.PhoneCreate):
    db_phone = models.Phone(number=phone.number)
    db.add(db_phone)
    db.commit()
    db.refresh(db_phone)
    return db_phone

# CRUD для видов деятельности
def create_activity(db: Session, activity: schemas.ActivityCreate):
    db_activity = models.Activity(**activity.dict())
    db.add(db_activity)
    db.commit()
    db.refresh(db_activity)
    return db_activity

def get_activity(db: Session, activity_id: int):
    return db.query(models.Activity).filter(models.Activity.id == activity_id).first()

def get_activities(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Activity).offset(skip).limit(limit).all()

# CRUD для зданий
def create_building(db: Session, building: schemas.BuildingCreate):
    db_building = models.Building(**building.dict())
    db.add(db_building)
    db.commit()
    db.refresh(db_building)
    return db_building

def get_building(db: Session, building_id: int):
    return db.query(models.Building).filter(models.Building.id == building_id).first()

def get_buildings(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Building).offset(skip).limit(limit).all()

# CRUD для организаций
def create_organization(db: Session, organization: schemas.OrganizationCreate):
    # Создаем телефоны
    phones = [models.Phone(number=phone) for phone in organization.phones]
    db.add_all(phones)
    db.flush()
    
    # Создаем организацию
    db_organization = models.Organization(
        name=organization.name,
        building_id=organization.building_id
    )
    db.add(db_organization)
    db.flush()
    
    # Добавляем телефоны и виды деятельности
    db_organization.phones = phones
    db_organization.activities = [
        db.query(models.Activity).get(activity_id)
        for activity_id in organization.activities
    ]
    
    db.commit()
    db.refresh(db_organization)
    return db_organization

def get_organization(db: Session, organization_id: int):
    return db.query(models.Organization).filter(models.Organization.id == organization_id).first()

def get_organizations(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Organization).offset(skip).limit(limit).all()

def get_organizations_by_building(db: Session, building_id: int):
    return db.query(models.Organization).filter(models.Organization.building_id == building_id).all()

def get_organizations_by_activity(db: Session, activity_id: int, include_children: bool = True):
    if include_children:
        # Получаем все дочерние виды деятельности
        activity = db.query(models.Activity).filter(models.Activity.id == activity_id).first()
        if not activity:
            return []
        
        # Получаем все дочерние ID (до 3 уровня)
        child_ids = get_child_activity_ids(db, activity_id, max_level=3)
        activity_ids = [activity_id] + child_ids
        
        # Получаем организации с указанными видами деятельности
        return db.query(models.Organization).join(
            models.Organization.activities
        ).filter(
            models.Activity.id.in_(activity_ids)
        ).all()
    else:
        return db.query(models.Organization).join(
            models.Organization.activities
        ).filter(
            models.Activity.id == activity_id
        ).all()

def get_child_activity_ids(db: Session, parent_id: int, max_level: int = 3, current_level: int = 1):
    if current_level >= max_level:
        return []
    
    children = db.query(models.Activity).filter(
        models.Activity.parent_id == parent_id
    ).all()
    
    child_ids = [child.id for child in children]
    for child in children:
        child_ids.extend(get_child_activity_ids(db, child.id, max_level, current_level + 1))
    
    return child_ids

def get_organizations_by_geo(db: Session, params: schemas.GeoSearchParams):
    if params.radius_km:
        # Поиск по радиусу
        return get_organizations_by_radius(db, params.center, params.radius_km)
    elif params.rectangle:
        # Поиск по прямоугольной области
        return get_organizations_by_rectangle(db, params.rectangle)
    return []

def get_organizations_by_radius(db: Session, center: schemas.GeoPoint, radius_km: float):
    # Используем формулу гаверсинусов для расчета расстояния
    organizations = []
    for org in db.query(models.Organization).all():
        distance = calculate_distance(
            center.latitude, center.longitude,
            org.building.latitude, org.building.longitude
        )
        if distance <= radius_km:
            organizations.append(org)
    return organizations

def get_organizations_by_rectangle(db: Session, rectangle: schemas.GeoRectangle):
    return db.query(models.Organization).join(
        models.Building
    ).filter(
        models.Building.latitude <= rectangle.north_west.latitude,
        models.Building.latitude >= rectangle.south_east.latitude,
        models.Building.longitude >= rectangle.north_west.longitude,
        models.Building.longitude <= rectangle.south_east.longitude
    ).all()

def search_organizations_by_name(db: Session, name: str):
    return db.query(models.Organization).filter(
        models.Organization.name.ilike(f"%{name}%")
    ).all()

def search_organizations_by_activity(db: Session, activity_name: str, include_children: bool = True):
    # Находим все виды деятельности, содержащие указанное название
    activities = db.query(models.Activity).filter(
        models.Activity.name.ilike(f"%{activity_name}%")
    ).all()
    
    if not activities:
        return []
    
    # Получаем все организации для найденных видов деятельности
    organizations = set()
    for activity in activities:
        orgs = get_organizations_by_activity(db, activity.id, include_children)
        organizations.update(orgs)
    
    return list(organizations)

def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Рассчитывает расстояние между двумя точками на Земле в километрах
    используя формулу гаверсинусов
    """
    R = 6371  # Радиус Земли в километрах

    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    return R * c 