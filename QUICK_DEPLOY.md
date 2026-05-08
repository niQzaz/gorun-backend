# 🚀 Быстрая шпаргалка - Деплой на Railway

## 📦 Подготовка (1 минута)

```bash
cd C:\Users\Amir\Downloads\app
git init
git add .
git commit -m "Initial commit"
```

## 🐙 GitHub (2 минуты)

1. Создай репозиторий: https://github.com/new
2. Название: `gorun-backend`
3. Private

```bash
git remote add origin https://github.com/YOUR_USERNAME/gorun-backend.git
git branch -M main
git push -u origin main
```

## 🚂 Railway (5 минут)

1. **Зайти:** https://railway.app
2. **Login with GitHub**
3. **New Project** → Deploy from GitHub → `gorun-backend`
4. **New** → Database → Add PostgreSQL
5. **Сервис** → Variables → RAW Editor:

```env
DATABASE_URL=${{Postgres.DATABASE_URL}}
SECRET_KEY=your-super-secret-key-12345
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

6. **Settings** → Networking → **Generate Domain**
7. Скопируй URL: `https://gorun-backend-production.up.railway.app`

## 📱 Android (3 минуты)

Найди `RetrofitClient.java` и измени:

```java
// HTTP
private static final String BASE_URL = "https://gorun-backend-production.up.railway.app/";

// WebSocket
private static final String WS_URL = "wss://gorun-backend-production.up.railway.app/";
```

## ✅ Проверка

```
https://твой-домен.railway.app
https://твой-домен.railway.app/docs
```

## 🔄 Обновление кода

```bash
git add .
git commit -m "Update"
git push
```

Railway автоматически задеплоит!

---

**Готово за 10 минут!** 🎉
