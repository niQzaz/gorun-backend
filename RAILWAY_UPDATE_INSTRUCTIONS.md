# Инструкция по обновлению репозитория | Repository Update Instructions

## Текущая структура проекта | Current Project Structure

```
C:\Users\Amir\Downloads\app\     # Корень проекта
├── app/                         # Папка с приложением
│   ├── __init__.py
│   ├── main.py
│   ├── database.py
│   ├── logger.py
│   ├── config.py
│   ├── chat_serialization.py
│   ├── crud/
│   ├── dependencies/
│   ├── models/
│   ├── routers/
│   ├── schemas/
│   ├── security/
│   ├── websocket/
│   ├── media/
│   └── logs/
├── requirements.txt             # Зависимости
├── Procfile                     # Команда запуска для Railway
├── runtime.txt                  # Версия Python
├── .gitignore                   # Игнорируемые файлы
└── README.md                    # Документация
```

## Шаги для обновления GitHub репозитория

### 1. Удалить старые файлы из корня (необязательно, но рекомендуется)

```bash
cd C:\Users\Amir\Downloads\app

# Удалить старые папки
rm -rf crud_old dependencies_old models_old routers_old schemas_old security_old websocket_old media_old

# Удалить старые файлы из корня
rm -f chat_serialization.py config.py database.py logger.py main.py __init__.py
```

### 2. Проверить изменения

```bash
git status
```

Должно показать:
- Новая папка `app/` с файлами
- Изменённый `Procfile`
- Изменённый `.gitignore`

### 3. Добавить все изменения

```bash
git add .
```

### 4. Закоммитить изменения

```bash
git commit -m "Реструктуризация проекта для Railway deployment

- Создана правильная структура с папкой app/
- Обновлён Procfile для запуска app.main:app
- Обновлён .gitignore
- Добавлены папки media/ и logs/ с .gitkeep
"
```

### 5. Запушить на GitHub

```bash
git push origin main
```

Если возникнет ошибка "rejected", используй:

```bash
git push origin main --force
```

⚠️ **ВНИМАНИЕ:** `--force` перезапишет историю на GitHub. Используй только если уверен!

## После пуша на GitHub

### 6. Railway автоматически задеплоит новую версию

1. Зайди на https://railway.app
2. Открой свой проект
3. Railway автоматически обнаружит изменения и начнёт новый деплой
4. Дождись завершения (обычно 2-3 минуты)

### 7. Проверь логи

В Railway:
1. Открой вкладку **Deployments**
2. Кликни на последний деплой
3. Открой **View Logs**

Должно быть:
```
✅ Starting application...
✅ Uvicorn running on http://0.0.0.0:PORT
✅ Application startup complete
```

### 8. Проверь работу API

Открой в браузере:
```
https://твой-проект.railway.app/
```

Должен вернуть:
```json
{"message": "Hello World"}
```

## Если что-то пошло не так

### Проблема: Railway не видит изменения

**Решение:**
1. В Railway нажми **Redeploy**
2. Или сделай пустой коммит:
```bash
git commit --allow-empty -m "Trigger redeploy"
git push origin main
```

### Проблема: Ошибка импорта модулей

**Решение:**
Проверь, что в `Procfile` написано:
```
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### Проблема: База данных не подключается

**Решение:**
1. В Railway открой **Variables**
2. Проверь, что есть переменная `DATABASE_URL`
3. Она должна начинаться с `postgresql://`

## Переменные окружения для Railway

В Railway добавь (если ещё не добавлены):

```
DATABASE_URL=postgresql://...  (автоматически от PostgreSQL плагина)
SECRET_KEY=твой-секретный-ключ-для-jwt
```

Для генерации SECRET_KEY:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## Готово! 🎉

После успешного деплоя твой API будет доступен по адресу:
```
https://твой-проект.railway.app
```

Используй этот URL в Android приложении для подключения к серверу.
