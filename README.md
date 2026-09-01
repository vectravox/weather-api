# Weather API

REST API сервис для получения информации о погоде с использованием данных от [Open-Meteo API](https://open-meteo.com/).

## 🚀 Основные возможности

- Получение текущей погоды по координатам
- Управление списком городов для отслеживания прогнозов
- Автоматическое обновление прогнозов в фоновом режиме (каждые 15 минут)
- Регистрация пользователей (многопользовательский режим)

## 🛠️ Технологии

- **Python 3.14+**
- **FastAPI** — веб-фреймворк
- **SQLAlchemy** — ORM для работы с БД
- **SQLite** — база данных
- **APScheduler** — фоновый планировщик задач
- **Pytest** — тестирование
- **Uvicorn** — ASGI сервер

## 📦 Установка и запуск

### Установка зависимостей и запуск сервера

#### ⚡ Способ 1: Через uv (рекомендуется)
Проект использует uv для быстрого управления зависимостями. Если у вас ещё не установлен uv:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Переходим в директорию проекта:
```bash
cd weather-api
```

Установка зависимостей:
```bash
uv sync
```

Запуск сервера:
```bash
uv run script.py
```

#### 🐍 Cпособ 2: Через pip (стандартный способ)
Переходим в директорию проекта:
```bash
cd weather-api
```

Создаем виртуальное окружение
```bash
python3 -m venv .venv
```

Активируем виртуальное окружение
```bash
source .venv/bin/activate
```

Установка зависимостей:
```bash
pip install -e .
```

Или вручную, если не поддерживается `-e .`:
```bash
pip install fastapi uvicorn sqlalchemy aiohttp apscheduler
```

Установка dev-зависимостей (для тестов)
```bash
pip install pytest httpx2
```

Деактивация виртуального окружения (после завершения работы)
```bash
deactivate
```
---
Сервер будет доступен по адресу: `http://127.0.0.1:8000`

## 📚 API Эндпоинты

### 👤 Пользователи

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| `POST` | `/users` | Регистрация нового пользователя |
| `POST` | `/users/{user_id}/cities` | Добавление города для отслеживания |
| `GET` | `/users/{user_id}/cities` | Получение списка городов пользователя |
| `GET` | `/users/{user_id}/cities/{city_name}/{hour}` | Получение прогноза на указанный час |

### 🌤️ Погода

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| `GET` | `/weather/current` | Текущая погода по координатам |

### 📖 Документация API

После запуска сервера доступна интерактивная документация:

- **Swagger UI**: `http://127.0.0.1:8000/docs`
- **ReDoc**: `http://127.0.0.1:8000/redoc`

## 💡 Примеры запросов с `curl`

| Символ | Значение |
|--------|----------|
| `{user_id}` | ID пользователя (целое число, например: `1`, `42`, `123`) |
| `{city_name}` | Название города (строка, например: `Moscow`, `London`, `Tokyo`) |
| `{hour}` | Час прогноза (целое число от `0` до `23`, например: `14`) |
| `{params}` | Список параметров через запятую: `temp`, `humidity`, `wind_speed`, `precipitation`, `pressure` |

### 1. Регистрация пользователя

**Шаблон запроса:**
```
POST /users
```

**Запрос:**
```bash
curl -X POST "http://127.0.0.1:8000/users" \
  -H "Content-Type: application/json" \
  -d '{"username": "alex123"}'
```

**Ответ:**
```json
{
  "id": 1,
  "username": "alex123",
  "created_at": "2026-07-20T10:30:00.123456"
}
```

---

### 2. Добавление города для отслеживания

**Шаблон запроса:**
```
POST /users/{user_id}/cities
```

**Запрос:**
```bash
curl -X POST "http://127.0.0.1:8000/users/1/cities" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Moscow",
    "lat": 55.7558,
    "lon": 37.6173
  }'
```

**Ответ:**
```json
{
  "id": 1,
  "name": "Moscow",
  "lat": 55.7558,
  "lon": 37.6173,
  "user_id": 1,
  "created_at": "2026-07-20T10:31:00.123456"
}
```

---

### 3. Получение списка городов пользователя

**Шаблон запроса:**
```
GET /users/{user_id}/cities
```

**Запрос:**
```bash
curl -X GET "http://127.0.0.1:8000/users/1/cities"
```

**Ответ:**
```json
[
  {
    "id": 1,
    "name": "Moscow",
    "lat": 55.7558,
    "lon": 37.6173,
    "user_id": 1,
    "created_at": "2026-07-20T10:31:00.123456"
  },
  {
    "id": 2,
    "name": "London",
    "lat": 51.5074,
    "lon": -0.1278,
    "user_id": 1,
    "created_at": "2026-07-20T10:32:00.123456"
  }
]
```

---

### 4. Получение прогноза на указанный час

**Шаблон запроса:**
```
GET /users/{user_id}/cities/{city_name}/{hour}?params={params}
```

**Запрос (все параметры):**
```bash
curl -X GET "http://127.0.0.1:8000/users/1/cities/Moscow/14?params=temp,humidity,wind_speed,precipitation,pressure"
```

**Ответ:**
```json
{
  "temp": 22.5,
  "humidity": 65,
  "wind_speed": 5.2,
  "precipitation": 0.0,
  "pressure": 1013.0
}
```

---

**Запрос (только температура и скорость ветра):**
```bash
curl -X GET "http://127.0.0.1:8000/users/1/cities/Moscow/14?params=temp,wind_speed"
```

**Ответ:**
```json
{
  "temp": 22.5,
  "wind_speed": 5.2
}
```

---

**Запрос (без параметров — вернутся параметры по умолчанию):**
```bash
curl -X GET "http://127.0.0.1:8000/users/1/cities/Moscow/14"
```

**Ответ (параметры по умолчанию настраиваются в `config.py`):**
```json
{
  "temp": 22.5,
  "wind_speed": 5.2,
  "pressure": 1013.0
}
```

---

### 5. Текущая погода по координатам

**Шаблон запроса:**
```
GET /weather/current?lat={lat}&lon={lon}&params={params}
```

**Запрос (параметры по умолчанию):**
```bash
curl -X GET "http://127.0.0.1:8000/weather/current?lat=55.7558&lon=37.6173"
```

**Ответ:**
```json
{
  "temp": 22.5,
  "wind_speed": 5.2,
  "pressure": 1013.0
}
```

---

**Запрос (кастомные параметры):**
```bash
curl -X GET "http://127.0.0.1:8000/weather/current?lat=55.7558&lon=37.6173&params=temp,humidity"
```

**Ответ:**
```json
{
  "temp": 22.5,
  "humidity": 65
}
```

## 🧪 Тестирование

### Запуск тестов

```bash
uv run pytest -v tests/
```
Или:
```bash
pytest -v tests/
```

### Что покрыто тестами

**Реализованные тесты для эндпоинта `/users`:**
- Успешная регистрация
- Конфликт при дубликате username (409)
- Валидация минимальной/максимальной длины
- Валидация допустимых символов
- Обработка пустого username
- Возврат корректных HTTP-статусов и структуры ответа

**Прочее:**
- API можно тестировать через Swagger UI по адресу `http://127.0.0.1/docs`

## 📁 Структура проекта

```
weather-api/
├── app/
│   ├── __init__.py
│   ├── config.py          # Конфигурация приложения
│   ├── crud.py            # CRUD операции с БД
│   ├── database.py        # Модели и подключение к БД
│   ├── main.py            # FastAPI приложение и эндпоинты
│   ├── models.py          # Pydantic модели
│   ├── scheduler.py       # Фоновый планировщик
│   └── services.py        # Бизнес-логика и работа с API
├── tests/
│   ├── __init__.py
│   ├── conftest.py        # Pytest фикстуры
│   └── test_users.py      # Тесты регистрации пользователей
├── script.py              # Точка входа
├── pyproject.toml         # Зависимости и настройки
└── README.md              # Вы здесь! 👋
```

## 🔧 Конфигурация

Основные настройки находятся в `app/config.py` (ниже перечислены только некоторые):

```python
# Файлы базы данных
APP_DATABASE_URL: str = "sqlite:///./weather.db"
SCHEDULER_DATABASE_URL: str = "sqlite:///./scheduler.db"

# Интервал обновления прогнозов
FORECAST_UPDATE_INTERVAL_MINUTES = 15

# Open-Meteo API
OPEN_METEO_URL: str = "https://api.open-meteo.com/v1/forecast"

# Валидация пользователей
USERNAME_MIN_LENGTH: int = 3
USERNAME_MAX_LENGTH: int = 50
USERNAME_PATTERN: str = r"^[a-zA-Z0-9_]+$"
```

## 📝 Примечания

- Для хранения данных используется SQLite — не требует дополнительной настройки
- База данных автоматически создаётся при первом запуске
- Прогноз для города загружается сразу при его добавлении
- Прогнозы обновляются автоматически каждые 15 минут
- Для хранения прогнозов и для запросов используется UTC время
- Прогноз доступен только на **текущие сутки** (с 00:00 до 23:59)
- API Open-Meteo не требует API-ключа и работает с ограничением 600 запросов в минуту с одного IP-адреса


## 🤝 Контакты

По всем вопросам:
- 🌐 [https://vk.ru/vectrax](https://vk.ru/vectrax)
- 💬 [https://t.me/vectravox](https://t.me/vectravox)
- ✉️ [vectravox@gmail.com](vectravox@gmail.com)
