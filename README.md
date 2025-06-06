# Organizations Directory API

API для работы с каталогом организаций. Позволяет управлять организациями, зданиями и видами деятельности.

## Требования

- Docker Desktop (установлен и запущен)
- Docker Compose

## Установка и запуск

1. Убедитесь, что Docker Desktop запущен:
   - Проверьте наличие иконки Docker в системном трее
   - Если Docker Desktop не запущен, запустите его
   - Если Docker Desktop не установлен, скачайте и установите с [официального сайта](https://www.docker.com/products/docker-desktop)

2. Клонируйте репозиторий:
```bash
git clone <repository-url>
cd <repository-directory>
```

3. Запустите приложение с помощью Docker Compose:
```bash
docker-compose up --build
```

Приложение будет доступно по адресу: http://localhost:8000

## Документация API

API документация доступна в следующих форматах:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Структура API

API разделено на следующие разделы:

### Организации
- `POST /api/organizations/` - Создание новой организации
- `GET /api/organizations/` - Получение списка организаций
- `GET /api/organizations/{organization_id}` - Получение информации об организации

### Здания
- `POST /api/buildings/` - Создание нового здания
- `GET /api/buildings/` - Получение списка зданий

### Виды деятельности
- `POST /api/activities/` - Создание нового вида деятельности
- `GET /api/activities/` - Получение списка видов деятельности

### Поиск
- `GET /api/organizations/building/{building_id}` - Поиск организаций по зданию
- `GET /api/organizations/activity/{activity_id}` - Поиск организаций по виду деятельности
- `POST /api/organizations/geo` - Геопоиск организаций
- `GET /api/organizations/search/name` - Поиск организаций по названию
- `GET /api/organizations/search/activity` - Поиск организаций по названию вида деятельности

## Обновление приложения

Для обновления приложения выполните следующие шаги:

1. Остановите текущие контейнеры:
```bash
docker-compose down
```

2. Получите последние изменения:
```bash
git pull
```

3. Пересоберите и запустите контейнеры:
```bash
docker-compose up --build
```

## База данных

База данных SQLite хранится в файле `organizations.db` и монтируется в контейнер как том. Это позволяет сохранять данные между перезапусками контейнера.

## Переменные окружения

- `DATABASE_URL` - URL для подключения к базе данных (по умолчанию: sqlite:///organizations.db)

## API Endpoints

### Организации
- POST /organizations/ - Создать новую организацию
- GET /organizations/ - Получить список организаций
- GET /organizations/{id} - Получить информацию об организации

### Здания
- POST /buildings/ - Создать новое здание
- GET /buildings/ - Получить список зданий
- GET /buildings/{id} - Получить информацию о здании

### Виды деятельности
- POST /activities/ - Создать новый вид деятельности
- GET /activities/ - Получить список видов деятельности
- GET /activities/{id} - Получить информацию о виде деятельности

### Телефоны
- POST /phones/ - Создать новый телефон 