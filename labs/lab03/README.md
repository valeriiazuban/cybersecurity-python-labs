Лабораторна робота №3: Прикладні бібліотеки Python для побудови вебзастосунків

Варіант 14: Реєстр ризиків контейнерної конфігурації

Автор: Студент групи (КБ-207) — (Зубань Валерія )

1. Опис предметної області

Застосунок є REST API сервісом для обліку результатів аудиту та перевірки безпеки конфігурації контейнерного середовища.

Категорії (categories):

image (id: 1) — безпека образів контейнерів;

runtime (id: 2) — налаштування середовища виконання;

secrets (id: 3) — перевірка витоків секретів та ключів доступу.

Одиниця вимірювання (unit): score (оцінка ризику).

Поріг реагування (threshold): 6.0.

Діапазон значення (value): від 0.0 до 10.0 включно.

Дозволені статуси (status): new, in_progress, done.

 2. Структура проєкту

cybersecurity-python-labs/
├── shared/
│   ├── __init__.py
│   └── student.py          # Дані про студента (ПІБ, група, варіант)
├── labs/
│   ├── __init__.py
│   └── lab03/
│       ├── __init__.py
│       ├── main.py         # Точка входу FastAPI, lifespan, системні маршрути
│       ├── database.py     # З'єднання з SQLite, увімкнення PRAGMA, створення таблиць
│       ├── schema.sql       # Схема бази даних (categories, records)
│       ├── repository.py   # Шар доступу до даних (параметризовані SQL-запити)
│       ├── schemas.py      # Pydantic-моделі для валідації вхідних та вихідних даних
│       ├── config.py       # Константи предметної області 14 варіанта
│       ├── seed.py         # Скрипт початкового заповнення бази з JSON в одній транзакції
│       ├── routers/
│       │   ├── __init__.py
│       │   ├── categories.py # Маршрути для управління категоріями
│       │   └── records.py    # Маршрути для управління записами знахідок аудиту
│       └── data/
│           ├── seed.json    # Навчальні дані 14 варіанта (додається до Git)
│           └── lab3.sqlite3 # База даних (ігнорується в .gitignore)
└── README.md


3. Основні класи та модулі

Pydantic-моделі (schemas.py):

CategoryCreate / CategoryRead: створення та повернення категорій (перевіряє довжину назви від 2 до 40 символів).

RecordBase: базова модель запису із жорсткою валідацією типів, рядків, статусів та забороною зайвих полів (extra="forbid").

RecordCreate / RecordReplace: моделі для POST та PUT запитів.

RecordRead: розширена модель відповіді, що включає id та згенероване category_name.

Ключові функції шару даних (repository.py):

get_connection() (database.py): створює підключення до SQLite та активує PRAGMA foreign_keys = ON.

get_records(...): виконує вибірку з фільтрацією (category_id, status, min_value, q), пагінацією (limit, offset) та JOIN назви категорії.

create_records_bulk(...): виконує атомарне додавання масиву записів у межах єдиної транзакції (with conn:).

4. Інструкція із запуску

Крок 1. Активація віртуального середовища та встановлення залежностей

# Активація віртуального середовища (Windows PowerShell)
.venv\Scripts\Activate.ps1

# Встановлення необхідних бібліотек
pip install fastapi uvicorn pydantic ruff


Крок 2. Ініціалізація та початкове заповнення бази даних

Виконується з кореня репозиторію:

python -m labs.lab03.seed


Скрипт створить файл labs/lab03/data/lab3.sqlite3, таблиці за schema.sql та додасть 3 категорії та 8 початкових записів із seed.json.

Крок 3. Запуск вебсервера FastAPI

uvicorn labs.lab03.main:app --reload --host 127.0.0.1 --port 8000


Сервіс буде доступний за адресою: http://127.0.0.1:8000

Інтерактивна документація Swagger UI: http://127.0.0.1:8000/docs

5. Приклади HTTP-запитів (cURL / Bash)

1. Перевірка доступності та даних студента

curl -i "http://127.0.0.1:8000/ping"
curl -i "http://127.0.0.1:8000/student"


2. Отримання категорій

curl -i "http://127.0.0.1:8000/categories"


3. Отримання записів із фільтрацією та пагінацією

curl -i "http://127.0.0.1:8000/records?category_id=1&status=new&limit=5&offset=0"


4. Створення нового запису

curl -i -X POST "http://127.0.0.1:8000/records" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "V14-NEW-01",
    "title": "Знахідка контейнерного аудиту 09",
    "category_id": 1,
    "value": 7.5,
    "status": "new"
  }'


5. Перевірка транзакційності (Bulk Rollback при конфлікті)

Запит містить один новий запис та один дублікат коду (V14-01). Очікується код 409 Conflict, а жоден із двох записів не зберігається в базу:

curl -i -X POST "http://127.0.0.1:8000/records/bulk" \
  -H "Content-Type: application/json" \
  -d '[
    {
      "code": "V14-ROLLBACK-TEST",
      "title": "Перший елемент пакета",
      "category_id": 1,
      "value": 4.0,
      "status": "new"
    },
    {
      "code": "V14-01",
      "title": "Дублікат коду з бази",
      "category_id": 2,
      "value": 5.0,
      "status": "new"
    }
  ]'


6. Перевірка якості коду (Ruff)

Для перевірки відповідності стандарту PEP 8 виконайте:

ruff check labs/lab03
ruff format --check labs/lab03