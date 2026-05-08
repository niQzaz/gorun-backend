# Деплой GoRun Backend на Render.com

## 🎯 Почему Render?

- ✅ **Полностью бесплатно** без привязки карты
- ✅ **PostgreSQL база** включена (1 GB)
- ✅ **HTTPS** автоматически
- ✅ **Автодеплой** из GitHub
- ✅ **750 часов/месяц** бесплатно

**Минус:** Сервис засыпает после 15 минут неактивности (первый запрос ~30 сек)

---

## 📋 Шаг 1: Подготовка GitHub репозитория

### 1.1 Создать репозиторий на GitHub

1. Зайди на https://github.com
2. Нажми **New repository**
3. Название: `gorun-backend`
4. Visibility: **Private** (рекомендую)
5. Нажми **Create repository**

### 1.2 Загрузить код

```bash
cd C:\Users\Amir\Downloads\app

# Инициализация git (если еще не сделано)
git init

# Создать .gitignore
echo "__pycache__/" > .gitignore
echo "*.pyc" >> .gitignore
echo ".env" >> .gitignore
echo "media/" >> .gitignore
echo ".venv/" >> .gitignore
echo "venv/" >> .gitignore

# Добавить все файлы
git add .

# Первый коммит
git commit -m "Initial commit - GoRun Backend"

# Подключить удаленный репозиторий (замени YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/gorun-backend.git

# Отправить код
git branch -M main
git push -u origin main
```

---

## 📋 Шаг 2: Регистрация на Render

1. Зайди на https://render.com
2. Нажми **Get Started for Free**
3. Зарегистрируйся через **GitHub** (проще всего)
4. Разреши доступ к репозиториям

---

## 📋 Шаг 3: Создание PostgreSQL базы данных

1. В Render Dashboard нажми **New +**
2. Выбери **PostgreSQL**
3. Заполни:
   - **Name:** `gorun-db`
   - **Database:** `gorun`
   - **User:** `gorun_user` (или оставь по умолчанию)
   - **Region:** `Frankfurt (EU Central)` (ближе к тебе)
   - **Plan:** **Free**
4. Нажми **Create Database**

⏳ Подожди 2-3 минуты, пока база создастся.

### 3.1 Скопировать Internal Database URL

После создания базы:
1. Открой созданную базу
2. Найди секцию **Connections**
3. Скопируй **Internal Database URL** (начинается с `postgresql://`)

Пример:
```
postgresql://gorun_user:xxxxx@dpg-xxxxx-a.frankfurt-postgres.render.com/gorun
```

**Важно:** Используй **Internal URL**, а не External!

---

## 📋 Шаг 4: Создание Web Service

1. В Render Dashboard нажми **New +**
2. Выбери **Web Service**
3. Нажми **Connect a repository**
4. Выбери репозиторий `gorun-backend`
5. Нажми **Connect**

### 4.1 Настройки сервиса

Заполни форму:

**Basic Settings:**
- **Name:** `gorun-backend`
- **Region:** `Frankfurt (EU Central)`
- **Branch:** `main`
- **Root Directory:** оставь пустым
- **Runtime:** `Python 3`
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

**Instance Type:**
- Выбери **Free**

### 4.2 Environment Variables (Переменные окружения)

Нажми **Add Environment Variable** и добавь:

1. **DATABASE_URL**
   - Value: `<Internal Database URL из шага 3.1>`
   - Пример: `postgresql://gorun_user:xxxxx@dpg-xxxxx-a.frankfurt-postgres.render.com/gorun`

2. **SECRET_KEY**
   - Value: `<сгенерируй случайную строку>`
   - Пример: `your-super-secret-key-change-this-in-production-12345`

3. **ALGORITHM**
   - Value: `HS256`

4. **ACCESS_TOKEN_EXPIRE_MINUTES**
   - Value: `1440`

### 4.3 Деплой

1. Нажми **Create Web Service**
2. ⏳ Подожди 5-10 минут, пока сервис развернется

---

## 📋 Шаг 5: Проверка работы

После успешного деплоя:

1. Render покажет URL твоего сервиса:
   ```
   https://gorun-backend.onrender.com
   ```

2. Открой в браузере:
   ```
   https://gorun-backend.onrender.com
   ```
   
   Должен вернуться JSON:
   ```json
   {"message": "Hello World"}
   ```

3. Проверь документацию API:
   ```
   https://gorun-backend.onrender.com/docs
   ```

---

## 📋 Шаг 6: Обновление Android приложения

Теперь нужно изменить URL в Android приложении.

### 6.1 Найти файл с BASE_URL

Обычно это:
- `RetrofitClient.java`
- `ApiConstants.java`
- `Constants.java`

### 6.2 Изменить URL

**Было:**
```java
private static final String BASE_URL = "http://192.168.1.100:8000/";
```

**Стало:**
```java
private static final String BASE_URL = "https://gorun-backend.onrender.com/";
```

### 6.3 Обновить WebSocket URL

**Было:**
```java
private static final String WS_URL = "ws://192.168.1.100:8000/";
```

**Стало:**
```java
private static final String WS_URL = "wss://gorun-backend.onrender.com/";
```

**Важно:** Используй `wss://` (с SSL), а не `ws://`

---

## 🔧 Управление сервисом

### Просмотр логов
1. Открой свой сервис в Render Dashboard
2. Перейди на вкладку **Logs**
3. Здесь видны все логи сервера в реальном времени

### Перезапуск сервиса
1. Открой сервис
2. Нажми **Manual Deploy** → **Deploy latest commit**

### Обновление кода
Просто сделай `git push` в репозиторий:
```bash
git add .
git commit -m "Update backend"
git push
```

Render автоматически задеплоит новую версию!

---

## ⚠️ Важные моменты

### 1. Сервис засыпает
После 15 минут неактивности сервис засыпает. Первый запрос разбудит его (~30 сек).

**Решение:** Можно настроить пинг каждые 10 минут (но это расходует часы).

### 2. Загрузка файлов (media/)
Render не сохраняет загруженные файлы между перезапусками.

**Решение:** Использовать облачное хранилище (Cloudinary, AWS S3, или Imgur API - все бесплатно).

### 3. База данных 1 GB
Бесплатная база ограничена 1 GB.

**Мониторинг:**
1. Открой базу в Render
2. Смотри **Disk Usage**

---

## 🎯 Альтернативы Render

Если Render не подойдет:

### Railway.app
- $5 кредитов/месяц бесплатно
- Не засыпает
- Проще настройка

**Инструкция:**
1. https://railway.app
2. Sign up with GitHub
3. New Project → Deploy from GitHub
4. Выбери репозиторий
5. Add PostgreSQL
6. Добавь переменные окружения
7. Deploy

### Fly.io
- Бесплатный план
- Не засыпает
- Требует карту (но не списывает)

---

## 📞 Помощь

Если что-то не работает:
1. Проверь логи в Render Dashboard
2. Убедись, что DATABASE_URL правильный (Internal URL)
3. Проверь, что все переменные окружения добавлены
4. Убедись, что requirements.txt содержит все зависимости

---

## ✅ Чек-лист

- [ ] Код загружен на GitHub
- [ ] PostgreSQL база создана на Render
- [ ] Web Service создан и задеплоен
- [ ] Переменные окружения добавлены
- [ ] Сервис отвечает на запросы
- [ ] Android приложение обновлено с новым URL
- [ ] WebSocket работает (wss://)

---

**Готово!** Теперь твой сервер работает 24/7 без домашнего ПК! 🎉
