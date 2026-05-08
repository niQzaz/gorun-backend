# ✅ Чек-лист деплоя GoRun Backend

## 📋 Подготовка (5 минут)

### 1. Проверка файлов проекта
- [x] `requirements.txt` создан
- [x] `Procfile` создан
- [x] `runtime.txt` создан
- [x] `.gitignore` создан
- [x] `README.md` создан
- [x] `config.py` использует переменные окружения

### 2. Проверка кода
- [ ] Сервер запускается локально без ошибок
- [ ] Все endpoints работают
- [ ] WebSocket подключается
- [ ] База данных подключена

```bash
# Проверить локально
cd C:\Users\Amir\Downloads\app
python -m uvicorn app.main:app --reload
# Открыть http://localhost:8000/docs
```

---

## 🐙 GitHub (10 минут)

### 3. Создание репозитория
- [ ] Зарегистрирован на GitHub
- [ ] Создан репозиторий `gorun-backend`
- [ ] Репозиторий Private (рекомендуется)

### 4. Загрузка кода
```bash
cd C:\Users\Amir\Downloads\app

# Инициализация
git init
git add .
git commit -m "Initial commit - GoRun Backend v1.1.0"

# Подключение к GitHub (замени YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/gorun-backend.git
git branch -M main
git push -u origin main
```

- [ ] Код загружен на GitHub
- [ ] Все файлы видны в репозитории

---

## 🚂 Railway.app (10 минут)

### 5. Регистрация
- [ ] Зайти на https://railway.app
- [ ] Login with GitHub
- [ ] Разрешить доступ к репозиториям

### 6. Создание проекта
- [ ] New Project
- [ ] Deploy from GitHub repo
- [ ] Выбрать `gorun-backend`
- [ ] Дождаться первого деплоя

### 7. Добавление PostgreSQL
- [ ] New → Database → Add PostgreSQL
- [ ] База создана (зеленая галочка)

### 8. Настройка переменных окружения
- [ ] Открыть сервис (не базу)
- [ ] Variables → RAW Editor
- [ ] Вставить:
```env
DATABASE_URL=${{Postgres.DATABASE_URL}}
SECRET_KEY=your-super-secret-key-change-this-12345
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```
- [ ] Update Variables
- [ ] Дождаться редеплоя

### 9. Настройка команды запуска
- [ ] Settings → Deploy
- [ ] Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- [ ] Сохранить

### 10. Генерация домена
- [ ] Settings → Networking
- [ ] Generate Domain
- [ ] Скопировать URL (например: `gorun-backend-production.up.railway.app`)

---

## ✅ Проверка работы (5 минут)

### 11. Тестирование API
- [ ] Открыть `https://ваш-домен.railway.app`
- [ ] Должен вернуться: `{"message": "Hello World"}`
- [ ] Открыть `https://ваш-домен.railway.app/docs`
- [ ] Swagger UI загружается

### 12. Проверка базы данных
- [ ] Открыть базу в Railway Dashboard
- [ ] Вкладка Data
- [ ] Таблицы созданы (users, messages, joint_run_challenges, и т.д.)

### 13. Проверка логов
- [ ] Открыть сервис
- [ ] Вкладка Deployments → Latest
- [ ] Логи без критических ошибок
- [ ] Видно "Application startup complete"

---

## 📱 Обновление Android (15 минут)

### 14. Найти файл с URL
Обычно это один из:
- [ ] `RetrofitClient.java`
- [ ] `ApiConstants.java`
- [ ] `Constants.java`

### 15. Обновить HTTP URL
```java
// Было
private static final String BASE_URL = "http://192.168.1.100:8000/";

// Стало (замени на свой домен)
private static final String BASE_URL = "https://gorun-backend-production.up.railway.app/";
```

### 16. Обновить WebSocket URL
```java
// Было
private static final String WS_URL = "ws://192.168.1.100:8000/";

// Стало (замени на свой домен)
private static final String WS_URL = "wss://gorun-backend-production.up.railway.app/";
```

**Важно:** Используй `wss://` (с SSL), а не `ws://`

### 17. Пересобрать Android приложение
- [ ] Build → Clean Project
- [ ] Build → Rebuild Project
- [ ] Установить на устройство

---

## 🧪 Финальное тестирование (10 минут)

### 18. Тест регистрации
- [ ] Открыть приложение
- [ ] Зарегистрировать нового пользователя
- [ ] Вход выполнен успешно

### 19. Тест основных функций
- [ ] Обновить профиль
- [ ] Загрузить аватар
- [ ] Добавить друга
- [ ] Отправить сообщение в чат
- [ ] Создать пробежку
- [ ] Создать совместный забег

### 20. Тест WebSocket
- [ ] Открыть чат
- [ ] Отправить сообщение
- [ ] Сообщение приходит в реальном времени
- [ ] Нет ошибок подключения

---

## 📊 Мониторинг (постоянно)

### 21. Настроить мониторинг
- [ ] Добавить Railway в закладки
- [ ] Проверять Usage раз в неделю
- [ ] Следить за расходом кредитов

### 22. Проверка работоспособности
Каждый день:
- [ ] Открыть `https://ваш-домен.railway.app/docs`
- [ ] Убедиться, что сервер отвечает

---

## 🎯 Дополнительно (опционально)

### 23. Настроить Cloudinary для файлов
- [ ] Зарегистрироваться на https://cloudinary.com
- [ ] Получить API ключи
- [ ] Интегрировать в backend
- [ ] Обновить Android для загрузки через Cloudinary

### 24. Настроить мониторинг ошибок
- [ ] Добавить Sentry (бесплатно)
- [ ] Настроить алерты

### 25. Оптимизация
- [ ] Добавить индексы в базу данных
- [ ] Настроить кеширование
- [ ] Добавить rate limiting

---

## ❌ Если что-то пошло не так

### Сервис не запускается
1. Проверь логи в Railway Dashboard
2. Убедись, что все переменные окружения добавлены
3. Проверь, что `DATABASE_URL` правильный
4. Убедись, что `requirements.txt` содержит все зависимости

### Android не подключается
1. Проверь, что используешь `https://` (не `http://`)
2. Убедись, что URL правильный (без лишних слешей)
3. Проверь, что сервер отвечает в браузере
4. Проверь логи Android (Logcat)

### WebSocket не работает
1. Используй `wss://` (не `ws://`)
2. Проверь endpoint: `/chat/ws/{conversation_id}`
3. Убедись, что токен передается правильно
4. Проверь логи сервера

### База данных не подключается
1. Проверь, что PostgreSQL создана в Railway
2. Убедись, что `DATABASE_URL` использует `${{Postgres.DATABASE_URL}}`
3. Проверь логи на ошибки подключения

---

## 📞 Помощь

**Документация:**
- Railway: https://docs.railway.app
- FastAPI: https://fastapi.tiangolo.com
- PostgreSQL: https://www.postgresql.org/docs

**Инструкции в проекте:**
- `DEPLOY_RAILWAY.md` - Подробная инструкция Railway
- `DEPLOY_RENDER.md` - Альтернатива (Render)
- `HOSTING_GUIDE.md` - Сравнение хостингов
- `README.md` - Описание проекта

---

## ✅ Финальная проверка

Все пункты выполнены? Поздравляю! 🎉

Твой сервер теперь:
- ✅ Работает 24/7 в облаке
- ✅ Не требует домашнего ПК
- ✅ Доступен из любой точки мира
- ✅ Автоматически обновляется при git push
- ✅ Имеет HTTPS и SSL
- ✅ Экономит электроэнергию

**Экономия:** ~100-150 кВт⋅ч/месяц (~500-750 рублей)

---

**Дата деплоя:** _______________  
**URL сервера:** _______________  
**Версия:** 1.1.0
