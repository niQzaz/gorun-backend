# GoRun Backend API

Backend сервер для мобильного приложения GoRun - социальной платформы для бега с GPS трекингом и совместными забегами.

## 🚀 Возможности

- 🔐 JWT аутентификация
- 👥 Система друзей (заявки, принятие/отклонение)
- 💬 Real-time чат через WebSocket (текст, изображения, shared runs)
- 🏃 GPS трекинг пробежек с метриками
- 🏆 Совместные забеги (челленджи по времени/дистанции с live обновлениями)
- 📊 История пробежек с маршрутами
- 👤 Профили пользователей с аватарами

## 🛠️ Технологии

- **Framework:** FastAPI
- **Database:** PostgreSQL
- **ORM:** SQLAlchemy
- **Auth:** JWT (python-jose)
- **WebSocket:** Native FastAPI WebSocket
- **Password:** Passlib with bcrypt

## 📦 Установка (локально)

### Требования
- Python 3.11+
- PostgreSQL 14+

### Шаги

1. **Клонировать репозиторий:**
```bash
git clone https://github.com/YOUR_USERNAME/gorun-backend.git
cd gorun-backend
```

2. **Создать виртуальное окружение:**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows
```

3. **Установить зависимости:**
```bash
pip install -r requirements.txt
```

4. **Создать базу данных:**
```sql
CREATE DATABASE gorun;
```

5. **Создать .env файл:**
```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/gorun
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

6. **Запустить сервер:**
```bash
uvicorn app.main:app --reload
```

Сервер запустится на http://localhost:8000

## 🌐 Деплой на хостинг

### Railway.app (Рекомендуется) ⭐
- Не засыпает
- $5 бесплатных кредитов/месяц
- Простая настройка

**Инструкция:** См. `DEPLOY_RAILWAY.md`

### Render.com
- Полностью бесплатно
- Засыпает после 15 минут неактивности

**Инструкция:** См. `DEPLOY_RENDER.md`

**Сравнение:** См. `HOSTING_GUIDE.md`

## 📚 API Документация

После запуска сервера:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## 🗂️ Структура проекта

```
app/
├── main.py                 # Точка входа
├── config.py              # Конфигурация
├── database.py            # Подключение к БД
├── models/                # SQLAlchemy модели
│   ├── user.py
│   ├── friend.py
│   ├── message.py
│   ├── joint_run.py
│   └── ...
├── routers/               # API endpoints
│   ├── auth_router.py
│   ├── user_router.py
│   ├── friend_router.py
│   ├── chat_router.py
│   ├── run_router.py
│   └── ...
├── crud/                  # CRUD операции
├── schemas/               # Pydantic схемы
├── security/              # JWT и хеширование
└── websocket/             # WebSocket manager
```

## 🔑 Основные endpoints

### Аутентификация
- `POST /auth/register` - Регистрация
- `POST /auth/login` - Вход

### Пользователи
- `GET /users/me` - Текущий пользователь
- `PUT /users/me` - Обновить профиль
- `POST /users/me/avatar` - Загрузить аватар

### Друзья
- `GET /friends` - Список друзей
- `POST /friends/request` - Отправить заявку
- `POST /friends/accept/{request_id}` - Принять заявку

### Чат
- `GET /chat` - Список чатов
- `GET /chat/{conversation_id}/messages` - Сообщения
- `POST /chat/send` - Отправить сообщение
- `WS /chat/ws/{conversation_id}` - WebSocket подключение

### Пробежки
- `POST /user-runs` - Сохранить пробежку
- `GET /user-runs/me` - Мои пробежки
- `POST /user-runs/{run_id}/share` - Поделиться пробежкой

### Совместные забеги
- `POST /chat/{conversation_id}/joint-runs` - Создать челлендж
- `POST /chat/joint-runs/{challenge_id}/accept` - Принять
- `POST /chat/joint-runs/{challenge_id}/ready` - Готов к старту
- `POST /chat/joint-runs/{challenge_id}/live` - Live обновление
- `GET /chat/joint-runs/{challenge_id}/route` - Получить маршруты

## 🔄 Последние обновления (v1.1.0)

### ✅ Исправления совместных пробежек
- Добавлено сохранение полных маршрутов участников
- Исправлена логика определения победителя
- Добавлена передача максимальной скорости
- Новый endpoint для получения маршрутов

**Подробнее:** См. `CHANGELOG_JOINT_RUN_FIXES.md`

## 🧪 Тестирование

```bash
# Запустить тесты (если есть)
pytest

# Проверить типы
mypy app/

# Форматирование
black app/
```

## 🔒 Безопасность

- JWT токены с истечением
- Bcrypt хеширование паролей
- CORS настройки
- SQL injection защита через ORM
- Валидация данных через Pydantic

## 📝 TODO

- [ ] Добавить rate limiting
- [ ] Настроить CORS для продакшена
- [ ] Добавить логирование
- [ ] Миграции через Alembic
- [ ] Unit тесты
- [ ] Интеграция с Cloudinary для файлов
- [ ] Пагинация для всех списков
- [ ] Индексы для оптимизации запросов

## 🤝 Вклад

Pull requests приветствуются! Для крупных изменений сначала откройте issue.

## 📄 Лицензия

MIT

## 📞 Контакты

- **Проект:** GoRun
- **Backend:** FastAPI + PostgreSQL
- **Android:** Java + Retrofit + Room + OSMDroid

---

**Версия:** 1.1.0  
**Дата:** 2026-05-08
