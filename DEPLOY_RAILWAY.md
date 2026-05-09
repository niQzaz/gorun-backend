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
git remote add origin https://github.com/niQzaz/gorun-backend.git
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


  File "/app/.venv/lib/python3.11/site-packages/uvicorn/main.py", line 579, in run
    server.run()
  File "/app/.venv/lib/python3.11/site-packages/uvicorn/server.py", line 65, in run
  File "/mise/installs/python/3.11.15/lib/python3.11/asyncio/runners.py", line 190, in run
  File "/app/.venv/lib/python3.11/site-packages/uvicorn/server.py", line 76, in _serve
    config.load()
  File "/app/.venv/lib/python3.11/site-packages/uvicorn/config.py", line 434, in load
  File "/app/.venv/lib/python3.11/site-packages/uvicorn/importer.py", line 22, in import_from_string
           ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/.venv/lib/python3.11/site-packages/click/core.py", line 1435, in main
Traceback (most recent call last):
             ^^^^^^
  File "/app/.venv/lib/python3.11/site-packages/click/core.py", line 1514, in __call__
  File "<frozen importlib._bootstrap>", line 1204, in _gcd_import
  File "<frozen importlib._bootstrap>", line 1176, in _find_and_load
  File "<frozen importlib._bootstrap>", line 1176, in _find_and_load
         ^^^^^^^^^^^^^^^^
  File "/app/.venv/lib/python3.11/site-packages/uvicorn/server.py", line 65, in run
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mise/installs/python/3.11.15/lib/python3.11/asyncio/runners.py", line 118, in run
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/.venv/lib/python3.11/site-packages/uvicorn/server.py", line 69, in serve
    config.load()
  File "<frozen importlib._bootstrap>", line 1204, in _gcd_import
  File "<frozen importlib._bootstrap>", line 1126, in _find_and_load_unlocked
  File "<frozen importlib._bootstrap>", line 1204, in _gcd_import
  File "/app/.venv/lib/python3.11/site-packages/uvicorn/importer.py", line 19, in import_from_string
    return _bootstrap._gcd_import(name[level:], package, level)
Traceback (most recent call last):
  File "/app/.venv/bin/uvicorn", line 8, in <module>
    sys.exit(main())
  File "/app/.venv/lib/python3.11/site-packages/click/core.py", line 1514, in __call__
           ^^^^^^^^^^^^^^^^^^^^^^^^^^
    rv = self.invoke(ctx)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/.venv/lib/python3.11/site-packages/click/core.py", line 853, in invoke
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mise/installs/python/3.11.15/lib/python3.11/asyncio/runners.py", line 190, in run
  File "/mise/installs/python/3.11.15/lib/python3.11/asyncio/runners.py", line 118, in run
    return self._loop.run_until_complete(task)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "uvloop/loop.pyx", line 1518, in uvloop.loop.Loop.run_until_complete
  File "/app/.venv/lib/python3.11/site-packages/uvicorn/server.py", line 69, in serve
    await self._serve(sockets)
    config.load()
  File "/app/.venv/lib/python3.11/site-packages/uvicorn/importer.py", line 22, in import_from_string
    raise exc from None
    module = importlib.import_module(module_str)
  File "/mise/installs/python/3.11.15/lib/python3.11/importlib/__init__.py", line 126, in import_module
  File "<frozen importlib._bootstrap>", line 1176, in _find_and_load
Traceback (most recent call last):
    sys.exit(main())
             ^^^^^^
  File "/app/.venv/lib/python3.11/site-packages/click/core.py", line 1435, in main
    rv = self.invoke(ctx)
  File "/app/.venv/lib/python3.11/site-packages/click/core.py", line 1298, in invoke
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/.venv/lib/python3.11/site-packages/uvicorn/main.py", line 412, in main
  File "/app/.venv/lib/python3.11/site-packages/uvicorn/main.py", line 579, in run
    server.run()
  File "/app/.venv/lib/python3.11/site-packages/uvicorn/server.py", line 65, in run
    return asyncio.run(self.serve(sockets=sockets))
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mise/installs/python/3.11.15/lib/python3.11/asyncio/runners.py", line 118, in run
    return self._loop.run_until_complete(task)
  File "uvloop/loop.pyx", line 1518, in uvloop.loop.Loop.run_until_complete
    await self._serve(sockets)
    config.load()
  File "/app/.venv/lib/python3.11/site-packages/uvicorn/config.py", line 434, in load
  File "/app/.venv/lib/python3.11/site-packages/uvicorn/importer.py", line 22, in import_from_string
  File "/app/.venv/lib/python3.11/site-packages/uvicorn/importer.py", line 19, in import_from_string
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mise/installs/python/3.11.15/lib/python3.11/importlib/__init__.py", line 126, in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
  File "<frozen importlib._bootstrap>", line 1126, in _find_and_load_unlocked
  File "<frozen importlib._bootstrap>", line 1204, in _gcd_import
  File "/app/.venv/lib/python3.11/site-packages/click/core.py", line 1435, in main
         ^^^^^^^^^^^^^^^^
  File "/app/.venv/lib/python3.11/site-packages/click/core.py", line 1298, in invoke
  File "/app/.venv/lib/python3.11/site-packages/click/core.py", line 853, in invoke
           ^^^^^^^^^^^^^^^^^^^^^^^^^^
    return callback(*args, **kwargs)
    run(
  File "/app/.venv/lib/python3.11/site-packages/uvicorn/server.py", line 65, in run
    return asyncio.run(self.serve(sockets=sockets))
  File "/mise/installs/python/3.11.15/lib/python3.11/asyncio/runners.py", line 190, in run
  File "/mise/installs/python/3.11.15/lib/python3.11/asyncio/runners.py", line 118, in run
    return self._loop.run_until_complete(task)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    self.loaded_app = import_from_string(self.app)
    raise exc from None
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    return _bootstrap._gcd_import(name[level:], package, level)
  File "/app/.venv/lib/python3.11/site-packages/click/core.py", line 1298, in invoke
  File "<frozen importlib._bootstrap>", line 1204, in _gcd_import
  File "<frozen importlib._bootstrap>", line 1176, in _find_and_load
  File "<frozen importlib._bootstrap>", line 241, in _call_with_frames_removed
  File "<frozen importlib._bootstrap>", line 1204, in _gcd_import
  File "<frozen importlib._bootstrap>", line 1176, in _find_and_load
  File "/app/.venv/bin/uvicorn", line 8, in <module>
             ^^^^^^
    return self.main(*args, **kwargs)
    rv = self.invoke(ctx)
    return ctx.invoke(self.callback, **ctx.params)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    server.run()
  File "/mise/installs/python/3.11.15/lib/python3.11/asyncio/runners.py", line 190, in run
    return runner.run(main)
  File "/app/.venv/lib/python3.11/site-packages/uvicorn/server.py", line 76, in _serve
           ^^^^^^^^^^^^^^^^
  File "/app/.venv/lib/python3.11/site-packages/uvicorn/config.py", line 434, in load
    self.loaded_app = import_from_string(self.app)
  File "uvloop/loop.pyx", line 1518, in uvloop.loop.Loop.run_until_complete