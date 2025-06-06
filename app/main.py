from fastapi import FastAPI, Depends, HTTPException, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from . import crud, models, schemas
from .database import engine, get_db
from .seed import seed_database
import os

# Создаем таблицы и заполняем базу данных при запуске
models.Base.metadata.create_all(bind=engine)
seed_database()

app = FastAPI(
    title="Organizations Directory API",
    description="""
    API для работы с каталогом организаций. 
    Позволяет управлять организациями, зданиями и видами деятельности.
    
    ## Основные возможности:
    * Управление организациями
    * Управление зданиями
    * Управление видами деятельности
    * Поиск организаций по различным параметрам
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Настройка статических файлов и шаблонов
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# Главная страница
@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Страница со списком организаций
@app.get("/organizations")
async def organizations(request: Request, db: Session = Depends(get_db)):
    organizations = crud.get_organizations(db)
    return templates.TemplateResponse(
        "organizations.html",
        {
            "request": request,
            "organizations": organizations,
            "message": None
        }
    )

# Страница добавления организации
@app.get("/organizations/new")
async def new_organization_form(request: Request, db: Session = Depends(get_db)):
    buildings = crud.get_buildings(db)
    activities = crud.get_activities(db)
    return templates.TemplateResponse(
        "new_organization.html",
        {
            "request": request,
            "buildings": buildings,
            "activities": activities,
            "message": None
        }
    )

# Обработка формы добавления организации
@app.post("/organizations/new")
async def create_organization(
    request: Request,
    name: str = Form(...),
    address: str = Form(...),
    phones: List[str] = Form(None),
    activities: List[int] = Form(None),
    db: Session = Depends(get_db)
):
    try:
        # Создаем новое здание
        building = models.Building(
            address=address,
            latitude=0.0,  # Временные координаты
            longitude=0.0  # Временные координаты
        )
        db.add(building)
        db.flush()
        
        # Создаем организацию
        organization = models.Organization(
            name=name,
            building_id=building.id
        )
        db.add(organization)
        db.flush()
        
        # Добавляем телефоны
        if phones:
            for phone_number in phones:
                if phone_number.strip():  # Проверяем, что номер не пустой
                    phone = models.Phone(number=phone_number)
                    db.add(phone)
                    db.flush()
                    organization.phones.append(phone)
        
        # Добавляем виды деятельности
        if activities:
            for activity_id in activities:
                activity = db.query(models.Activity).get(activity_id)
                if activity:
                    organization.activities.append(activity)
        
        db.commit()
        return RedirectResponse(url="/organizations", status_code=303)
    except Exception as e:
        db.rollback()
        return templates.TemplateResponse(
            "new_organization.html",
            {
                "request": request,
                "message": {"type": "danger", "text": f"Ошибка при создании организации: {str(e)}"}
            }
        )

# API эндпоинты
@app.post("/api/organizations/", 
    response_model=schemas.Organization,
    tags=["Организации"],
    summary="Создать новую организацию",
    description="Создает новую организацию с указанными параметрами"
)
def create_organization_api(organization: schemas.OrganizationCreate, db: Session = Depends(get_db)):
    return crud.create_organization(db=db, organization=organization)

@app.get("/api/organizations/", 
    response_model=List[schemas.Organization],
    tags=["Организации"],
    summary="Получить список организаций",
    description="Возвращает список всех организаций с возможностью пагинации"
)
def read_organizations_api(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    organizations = crud.get_organizations(db, skip=skip, limit=limit)
    return organizations

@app.get("/api/organizations/{organization_id}", 
    response_model=schemas.Organization,
    tags=["Организации"],
    summary="Получить информацию об организации",
    description="Возвращает подробную информацию об организации по её ID"
)
def read_organization_api(organization_id: int, db: Session = Depends(get_db)):
    db_organization = crud.get_organization(db, organization_id=organization_id)
    if db_organization is None:
        raise HTTPException(status_code=404, detail="Organization not found")
    return db_organization

@app.post("/api/buildings/", 
    response_model=schemas.Building,
    tags=["Здания"],
    summary="Создать новое здание",
    description="Создает новое здание с указанными параметрами"
)
def create_building_api(building: schemas.BuildingCreate, db: Session = Depends(get_db)):
    return crud.create_building(db=db, building=building)

@app.get("/api/buildings/", 
    response_model=List[schemas.Building],
    tags=["Здания"],
    summary="Получить список зданий",
    description="Возвращает список всех зданий с возможностью пагинации"
)
def read_buildings_api(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    buildings = crud.get_buildings(db, skip=skip, limit=limit)
    return buildings

@app.post("/api/activities/", 
    response_model=schemas.Activity,
    tags=["Виды деятельности"],
    summary="Создать новый вид деятельности",
    description="Создает новый вид деятельности с указанными параметрами"
)
def create_activity_api(activity: schemas.ActivityCreate, db: Session = Depends(get_db)):
    return crud.create_activity(db=db, activity=activity)

@app.get("/api/activities/", 
    response_model=List[schemas.Activity],
    tags=["Виды деятельности"],
    summary="Получить список видов деятельности",
    description="Возвращает список всех видов деятельности с возможностью пагинации"
)
def read_activities_api(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    activities = crud.get_activities(db, skip=skip, limit=limit)
    return activities

@app.get("/organizations/{organization_id}")
async def organization_details(
    request: Request,
    organization_id: int,
    db: Session = Depends(get_db)
):
    organization = crud.get_organization(db, organization_id)
    if not organization:
        return templates.TemplateResponse(
            "organization_details.html",
            {
                "request": request,
                "message": {"type": "danger", "text": "Организация не найдена"}
            }
        )
    
    return templates.TemplateResponse(
        "organization_details.html",
        {
            "request": request,
            "organization": organization,
            "message": None
        }
    )

# Страница со списком адресов
@app.get("/buildings")
async def buildings(request: Request, db: Session = Depends(get_db)):
    buildings = crud.get_buildings(db)
    return templates.TemplateResponse(
        "buildings.html",
        {
            "request": request,
            "buildings": buildings,
            "message": None
        }
    )

# API эндпоинты для поиска организаций
@app.get("/api/organizations/building/{building_id}", 
    response_model=List[schemas.Organization],
    tags=["Поиск"],
    summary="Поиск организаций по зданию",
    description="Возвращает список организаций, расположенных в указанном здании"
)
def get_organizations_by_building_api(building_id: int, db: Session = Depends(get_db)):
    organizations = crud.get_organizations_by_building(db, building_id)
    return organizations

@app.get("/api/organizations/activity/{activity_id}", 
    response_model=List[schemas.Organization],
    tags=["Поиск"],
    summary="Поиск организаций по виду деятельности",
    description="Возвращает список организаций с указанным видом деятельности"
)
def get_organizations_by_activity_api(
    activity_id: int,
    include_children: bool = True,
    db: Session = Depends(get_db)
):
    organizations = crud.get_organizations_by_activity(db, activity_id, include_children)
    return organizations

@app.post("/api/organizations/geo", 
    response_model=List[schemas.Organization],
    tags=["Поиск"],
    summary="Геопоиск организаций",
    description="Возвращает список организаций в указанном географическом радиусе"
)
def get_organizations_by_geo_api(
    params: schemas.GeoSearchParams,
    db: Session = Depends(get_db)
):
    organizations = crud.get_organizations_by_geo(db, params)
    return organizations

@app.get("/api/organizations/search/name", 
    response_model=List[schemas.Organization],
    tags=["Поиск"],
    summary="Поиск организаций по названию",
    description="Возвращает список организаций, чьи названия содержат указанную строку"
)
def search_organizations_by_name_api(
    name: str,
    db: Session = Depends(get_db)
):
    organizations = crud.search_organizations_by_name(db, name)
    return organizations

@app.get("/api/organizations/search/activity", 
    response_model=List[schemas.Organization],
    tags=["Поиск"],
    summary="Поиск организаций по названию вида деятельности",
    description="Возвращает список организаций, чьи виды деятельности содержат указанную строку"
)
def search_organizations_by_activity_api(
    activity_name: str,
    include_children: bool = True,
    db: Session = Depends(get_db)
):
    organizations = crud.search_organizations_by_activity(db, activity_name, include_children)
    return organizations 