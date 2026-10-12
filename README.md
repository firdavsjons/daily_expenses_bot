# 💰 Telegram-бот для учёта личных доходов и расходов (expenses_bot)

Полноценный Telegram-бот на Python (aiogram 3.x) для автоматизированного учёта личных финансов. Поддерживает работу с 3 валютами (TJS, RUB, USD), автоматический умный разбор сообщений на естественном языке, бюджетирование, регулярные платежи, графики matplotlib и экспорты в Excel.

---

## 🛠 Стек технологий

- **Python**: 3.11+
- **Telegram Bot Framework**: `aiogram 3.x`
- **ORM & DB**: `SQLAlchemy 2.x (asyncio)` + `asyncpg` + `PostgreSQL`
- **Миграции БД**: `Alembic`
- **Планировщик задач**: `APScheduler` (обновление курсов валют, автооплата подписок, вечернее напоминание)
- **Визуализация отчётов**: `matplotlib` (круговые диаграммы расходов)
- **Экспорт данных**: `pandas` + `openpyxl` (выгрузка в Excel `.xlsx`)
- **HTTP Клиент**: `httpx` (запросы к Frankfurter API / NBT)

---

## 📁 Структура проекта

```
expenses_bot/
├── .env.example               # Шаблон переменных окружения
├── requirements.txt           # Зависимости Python
├── alembic.ini                # Конфигурация Alembic
├── alembic/                   # Файлы миграций базы данных
│   └── versions/
│       └── 001_initial_schema.py
├── bot/
│   ├── main.py                # Главная точка входа бота
│   ├── config.py              # Загрузка и валидация конфигураций
│   ├── models.py              # Модели SQLAlchemy 2.x
│   ├── database.py            # Настройка асинхронной БД и автосоздание БД
│   ├── seed.py                # Сидер базовых категорий
│   ├── parser.py              # NLP-разбор свободного текста
│   ├── keyboards.py           # Игровые/Инлайн клавиатуры
│   ├── handlers/              # Роутеры обработчиков aiogram
│   │   ├── start.py
│   │   ├── transactions.py
│   │   ├── categories.py
│   │   ├── reports.py
│   │   ├── budgets.py
│   │   ├── currency.py
│   │   └── recurring.py
│   └── services/              # Сервисы бизнес-логики
│       ├── currency_service.py # Получение курсов валют
│       ├── report_service.py   # Генерация отчётов, графиков и Excel
│       └── scheduler.py        # Фоновые задачи APScheduler
├── tests/
│   └── test_parser.py         # Юнит-тесты парсера текста
└── README.md
```

---

## 🚀 Быстрый запуск

### 1. Клонирование и настройка виртуального окружения

```bash
git clone <repository_url>
cd daily_expenses_bot

python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 2. Настройка переменных окружения

Скопируйте шаблон:

```bash
cp .env.example .env
```

Затем укажите собственные значения в `.env`:

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_postgres_password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=expenses_bot
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
DEFAULT_CURRENCY=TJS
```

Файл `.env` содержит секреты и не публикуется в Git.

### 3. Автоматическое создание базы данных и применение миграций

Бот автоматически проверяет наличие базы данных `expenses_bot` в PostgreSQL и при отсутствии сам создаёт её (подключаясь к системной базе `postgres`).

Для ручной инициализации и применения миграций Alembic:

```bash
source venv/bin/activate
alembic upgrade head
```

### 4. Запуск юнит-тестов парсера

```bash
source venv/bin/activate
pytest tests/test_parser.py
```

### 5. Запуск Telegram-бота

```bash
source venv/bin/activate
python3 -m bot.main
```

---

## 💡 Принципы работы и решения

1. **Разбор текста (NLP)**:
   - Модуль `bot/parser.py` извлекает сумму (целую или дробную), определяет валюту по ключевым словам (например, `см`, `сом`, `руб`, `$`), сопоставляет слова с категориями и выделяет оставшийся текст в комментарий.
   - Если парсер не уверен в категории, бот выводит удобную Inline-клавиатуру выбора категорий.

2. **Работа с курсами валют**:
   - Бот автоматически каждые сутки в 00:05 запрашивает актуальные курсы Национального Банка Таджикистана (NBT) через Frankfurter API.
   - При добавлении операции в валюте (например, USD или RUB) сумма пересчитывается в базовую валюту пользователя и сохраняется вместе с курсом на момент совершения операции.

3. **Бюджетирование и уведомления**:
   - При превышении 80% или 100% месячного лимита по категории бот мгновенно отправляет предупреждение.

4. **Фоновые регулярные платежи**:
   - APScheduler каждые 10 минут проверяет регулярные списывания (`daily`, `weekly`, `monthly`) и автоматически создает операции с отправкой уведомлений пользователю.
