# Деплой на Railway.app (Рекомендуется!)

## 🎯 Почему Railway?

- ✅ **$5 бесплатных кредитов/месяц** (без карты!)
- ✅ **НЕ засыпает** (в отличие от Render)
- ✅ **PostgreSQL включен**
- ✅ **Проще настройка** чем Render
- ✅ **Быстрее деплой**

**Минус:** Кредиты могут закончиться при очень активном использовании (но $5 хватает на месяц для небольшого проекта)

---

## 📋 Быстрый старт (5 минут)

### Шаг 1: Загрузить код на GitHub

```bash
cd C:\Users\Amir\Downloads\app

# Инициализация (если еще не сделано)
git init
git add .
git commit -m "Initial commit"

# Создай репозиторий на GitHub и подключи
git remote add origin https://github.com/YOUR_USERNAME/gorun-backend.git
git branch -M main
git push -u origin main
```

---

### Шаг 2: Регистрация на Railway

1. Зайди на https://railway.app
2. Нажми **Login**
3. Выбери **Login with GitHub**
4. Разреши доступ

---

### Шаг 3: Создание проекта

1. Нажми **New Project**
2. Выбери **Deploy from GitHub repo**
3. Выбери репозиторий `gorun-backend`
4. Railway автоматически определит Python проект

---

### Шаг 4: Добавить PostgreSQL

1. В проекте нажми **New**
2. Выбери **Database** → **Add PostgreSQL**
3. База создастся автоматически

---

### Шаг 5: Настроить переменные окружения

1. Открой свой сервис (не базу данных)
2. Перейди на вкладку **Variables**
3. Нажми **RAW Editor**
4. Вставь:

```env
DATABASE_URL=${{Postgres.DATABASE_URL}}
SECRET_KEY=your-super-secret-key-change-this-12345
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

**Важно:** `${{Postgres.DATABASE_URL}}` автоматически подставит URL базы!

5. Нажми **Update Variables**

---

### Шаг 6: Настроить деплой

1. Перейди на вкладку **Settings**
2. В секции **Deploy** найди **Start Command**
3. Добавь:
   ```
   uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```
4. Нажми **Deploy**

---

### Шаг 7: Получить URL

1. Перейди на вкладку **Settings**
2. В секции **Networking** нажми **Generate Domain**
3. Railway создаст домен типа:
   ```
   gorun-backend-production.up.railway.app
   ```

---

### Шаг 8: Проверить работу

Открой в браузере:
```
https://gorun-backend-production.up.railway.app
```

Должен вернуться:
```json
{"message": "Hello World"}
```

Проверь API документацию:
```
https://gorun-backend-production.up.railway.app/docs
```

---

## 📱 Обновление Android приложения

Найди файл с BASE_URL (обычно `RetrofitClient.java`) и измени:

```java
// Было
private static final String BASE_URL = "http://192.168.1.100:8000/";

// Стало
private static final String BASE_URL = "https://gorun-backend-production.up.railway.app/";
```

WebSocket URL:
```java
// Было
private static final String WS_URL = "ws://192.168.1.100:8000/";

// Стало
private static final String WS_URL = "wss://gorun-backend-production.up.railway.app/";
```

---

## 🔧 Управление

### Просмотр логов
1. Открой проект в Railway
2. Кликни на сервис
3. Вкладка **Deployments** → выбери последний деплой
4. Логи в реальном времени

### Обновление кода
Просто сделай git push:
```bash
git add .
git commit -m "Update"
git push
```

Railway автоматически задеплоит!

### Мониторинг использования
1. Открой проект
2. Вкладка **Usage**
3. Смотри сколько кредитов осталось

---

## 💰 Управление кредитами

### Сколько хватит $5?

Примерный расход:
- **CPU:** ~$0.000463/минуту
- **RAM (512MB):** ~$0.000231/минуту
- **Итого:** ~$0.0007/минуту = **$1/день** при постоянной работе

**Оптимизация:**
- Сервис работает только когда есть запросы
- При низкой нагрузке хватит на весь месяц
- Можно добавить карту для $5/месяц (но это уже платно)

---

## 🎯 Сравнение с Render

| Параметр | Railway | Render |
|----------|---------|--------|
| Засыпает? | ❌ Нет | ✅ Да (15 мин) |
| Карта нужна? | ❌ Нет | ❌ Нет |
| Бесплатно | $5 кредитов | 750 часов |
| База данных | ✅ Да | ✅ Да |
| Настройка | Проще | Сложнее |

**Вывод:** Railway лучше для активного использования, Render — для редких запросов.

---

## ⚠️ Важно

### 1. Загрузка файлов
Railway не сохраняет загруженные файлы между деплоями.

**Решение:** Использовать Cloudinary (бесплатно):
1. https://cloudinary.com
2. Зарегистрируйся
3. Получи API ключи
4. Интегрируй в backend

### 2. Мониторинг кредитов
Следи за расходом в разделе **Usage**. Если кредиты заканчиваются — сервис остановится.

---

## ✅ Чек-лист

- [ ] Код на GitHub
- [ ] Проект создан на Railway
- [ ] PostgreSQL добавлена
- [ ] Переменные окружения настроены
- [ ] Домен сгенерирован
- [ ] Сервис отвечает
- [ ] Android обновлен

---

**Готово!** Сервер работает 24/7 без засыпания! 🚀
