from sqlalchemy.orm import Session
from sqlalchemy import func
from .models import Base, Activity, Building, Organization, Phone
from .database import engine, SessionLocal

def seed_database():
    # Создаем таблицы
    Base.metadata.create_all(bind=engine)
    
    # Создаем сессию
    db = SessionLocal()
    
    try:
        # Создаем виды деятельности с иерархией
        food = Activity(name="Еда", level=1)
        db.add(food)
        db.flush()

        meat = Activity(name="Мясная продукция", parent_id=food.id, level=2)
        dairy = Activity(name="Молочная продукция", parent_id=food.id, level=2)
        db.add_all([meat, dairy])
        db.flush()

        beef = Activity(name="Говядина", parent_id=meat.id, level=3)
        pork = Activity(name="Свинина", parent_id=meat.id, level=3)
        milk = Activity(name="Молоко", parent_id=dairy.id, level=3)
        cheese = Activity(name="Сыр", parent_id=dairy.id, level=3)
        db.add_all([beef, pork, milk, cheese])
        db.flush()
        
        # Создаем здания
        buildings = [
            Building(
                address="г. Москва, ул. Ленина 1, офис 3",
                latitude=55.7558,
                longitude=37.6173
            ),
            Building(
                address="г. Москва, ул. Блюхера, 32/1",
                latitude=55.7517,
                longitude=37.6178
            )
        ]
        db.add_all(buildings)
        db.flush()
        
        # Создаем организации
        organizations = [
            Organization(
                name='ООО "Рога и Копыта"',
                building_id=buildings[0].id
            ),
            Organization(
                name='Мясной магазин',
                building_id=buildings[0].id
            ),
            Organization(
                name='Молочный магазин',
                building_id=buildings[1].id
            )
        ]
        db.add_all(organizations)
        db.flush()
        
        # Добавляем телефоны
        phones = [
            Phone(number="2-222-222", organization_id=organizations[0].id),
            Phone(number="3-333-333", organization_id=organizations[0].id),
            Phone(number="8-923-666-13-13", organization_id=organizations[0].id),
            Phone(number="+7 (999) 111-22-33", organization_id=organizations[1].id),
            Phone(number="+7 (999) 444-55-66", organization_id=organizations[1].id),
            Phone(number="+7 (999) 777-88-99", organization_id=organizations[2].id)
        ]
        db.add_all(phones)
        db.flush()
        
        # Связываем организации с видами деятельности
        organizations[0].activities = [meat, beef, pork]
        organizations[1].activities = [meat, beef, pork]
        organizations[2].activities = [dairy, milk, cheese]
        
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    seed_database() 