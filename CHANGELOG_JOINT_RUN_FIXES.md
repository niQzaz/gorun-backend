# Исправления совместных пробежек - Changelog

**Дата:** 2026-05-08  
**Версия:** 1.1.0

## 🎯 Цель обновления

Исправление критических проблем с сохранением и отображением данных совместных пробежек.

---

## ✅ Исправленные проблемы

### 1. **Сохранение полных маршрутов участников**
- ❌ **Было:** Сохранялась только последняя координата каждого участника
- ✅ **Стало:** Все точки маршрута сохраняются в новую таблицу `joint_run_challenge_route_points`

### 2. **Определение победителя**
- ❌ **Было:** При равных дистанциях победитель не определялся (winner_id = NULL)
- ✅ **Стало:** При равных дистанциях сравнивается время, поддержка ничьей

### 3. **Максимальная скорость участников**
- ❌ **Было:** Максимальная скорость не передавалась через API
- ✅ **Стало:** Добавлены поля `creator_max_speed_kmh` и `opponent_max_speed_kmh`

### 4. **API для получения маршрутов**
- ❌ **Было:** Невозможно получить полный маршрут после завершения забега
- ✅ **Стало:** Новый endpoint `GET /chat/joint-runs/{challenge_id}/route`

---

## 📦 Изменения в Backend

### Новые файлы:
1. **`models/joint_run_route_point.py`** - Модель для точек маршрута
2. **`crud/joint_run_crud.py`** - CRUD операции для маршрутов
3. **`migrations/add_joint_run_route_points.sql`** - SQL миграция

### Измененные файлы:
1. **`models/joint_run.py`**
   - Добавлены поля: `creator_max_speed_kmh`, `opponent_max_speed_kmh`
   - Добавлена связь: `route_points` relationship

2. **`routers/chat_router.py`**
   - Модифицирован `POST /joint-runs/{challenge_id}/live` - сохраняет точки маршрута
   - Добавлен `GET /joint-runs/{challenge_id}/route` - возвращает полные маршруты
   - Исправлена функция `mark_joint_run_finished_if_needed()` - корректное определение победителя

3. **`schemas/chat_schema.py`**
   - Добавлено поле `max_speed_kmh` в `JointRunLiveUpdate`
   - Добавлены поля `creator_max_speed_kmh`, `opponent_max_speed_kmh` в `JointRunPreview`
   - Новые схемы: `RoutePointPreview`, `JointRunRouteResponse`

4. **`chat_serialization.py`**
   - Добавлена сериализация `max_speed_kmh` полей

5. **`main.py`**
   - Импорт новой модели `joint_run_route_point`
   - Добавлены миграции для новых полей

---

## 🗄️ Изменения в базе данных

### Новая таблица:
```sql
CREATE TABLE joint_run_challenge_route_points (
    id SERIAL PRIMARY KEY,
    challenge_id INTEGER NOT NULL REFERENCES joint_run_challenges(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    sequence_index INTEGER NOT NULL,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    elapsed_time_millis INTEGER NOT NULL,
    distance_meters DOUBLE PRECISION NOT NULL
);
```

### Новые поля в `joint_run_challenges`:
- `creator_max_speed_kmh` (DOUBLE PRECISION, nullable)
- `opponent_max_speed_kmh` (DOUBLE PRECISION, nullable)

### Индексы:
- `joint_run_route_challenge_user_idx` на (challenge_id, user_id)
- `joint_run_route_sequence_idx` на (challenge_id, user_id, sequence_index)

---

## 🚀 Инструкции по обновлению

### Шаг 1: Обновление Backend

```bash
cd C:\Users\Amir\Downloads\app

# Остановить сервер (если запущен)
# Ctrl+C

# Применить миграцию вручную (опционально, если нужно сохранить существующие данные)
psql -U your_user -d your_database -f migrations/add_joint_run_route_points.sql

# Или просто запустить сервер - миграции применятся автоматически
python -m uvicorn app.main:app --reload
```

### Шаг 2: Проверка миграций

После запуска сервера проверьте логи:
- ✅ Таблица `joint_run_challenge_route_points` создана
- ✅ Поля `creator_max_speed_kmh` и `opponent_max_speed_kmh` добавлены

### Шаг 3: Обновление Android (требуется)

**Необходимые изменения в Android:**

1. **Обновить `JointRunLiveUpdateRequest.java`:**
```java
@SerializedName("max_speed_kmh")
private final Double maxSpeedKmh;
```

2. **Обновить `ChatJointRun.java`:**
```java
@SerializedName("creator_max_speed_kmh")
private Double creatorMaxSpeedKmh;

@SerializedName("opponent_max_speed_kmh")
private Double opponentMaxSpeedKmh;
```

3. **Модифицировать `ChatRepository.updateJointRunLive()`:**
```java
public void updateJointRunLive(int challengeId,
                               Double latitude,
                               Double longitude,
                               double distanceMeters,
                               long durationMillis,
                               Double maxSpeedKmh,  // Новый параметр
                               RepositoryCallback<ChatMessage> callback)
```

4. **Добавить в `ChatApi.java`:**
```java
@GET("chat/joint-runs/{challenge_id}/route")
Call<JointRunRouteResponse> getJointRunRoute(@Path("challenge_id") int challengeId);
```

5. **Создать модель `JointRunRouteResponse.java`:**
```java
public class JointRunRouteResponse {
    @SerializedName("challenge_id")
    private int challengeId;
    
    @SerializedName("creator_id")
    private int creatorId;
    
    @SerializedName("opponent_id")
    private int opponentId;
    
    @SerializedName("creator_route")
    private List<RoutePoint> creatorRoute;
    
    @SerializedName("opponent_route")
    private List<RoutePoint> opponentRoute;
}
```

---

## 🧪 Тестирование

### Backend тесты:

1. **Создание совместного забега:**
```bash
POST /chat/{conversation_id}/joint-runs
{
  "mode": "distance",
  "target_distance_meters": 5000,
  "client_message_id": "test123"
}
```

2. **Live update с координатами:**
```bash
POST /chat/joint-runs/{challenge_id}/live
{
  "latitude": 55.7558,
  "longitude": 37.6173,
  "distance_meters": 1500,
  "duration_millis": 300000,
  "max_speed_kmh": 12.5
}
```

3. **Получение маршрута:**
```bash
GET /chat/joint-runs/{challenge_id}/route
```

Ожидаемый ответ:
```json
{
  "challenge_id": 1,
  "creator_id": 10,
  "opponent_id": 20,
  "creator_route": [
    {
      "sequence_index": 0,
      "latitude": 55.7558,
      "longitude": 37.6173,
      "elapsed_time_millis": 0,
      "distance_meters": 0
    },
    ...
  ],
  "opponent_route": [...]
}
```

---

## 📊 Влияние на производительность

### Хранилище:
- **До:** ~200 байт на забег (только финальные координаты)
- **После:** ~50 байт × количество точек × 2 участника
- **Пример:** Забег 30 минут, обновления каждые 3 сек = 600 точек × 2 = 1200 точек × 50 байт = **~60 KB на забег**

### Рекомендации:
- Добавить очистку старых маршрутов (>30 дней)
- Рассмотреть сжатие координат для длинных забегов
- Добавить пагинацию при получении маршрутов (если >1000 точек)

---

## 🔄 Обратная совместимость

✅ **Полностью обратно совместимо:**
- Старые клиенты могут работать без обновления
- Новые поля опциональны (nullable)
- Существующие endpoint'ы не изменились

⚠️ **Рекомендуется обновить Android:**
- Для получения максимальной скорости соперника
- Для доступа к полным маршрутам после завершения

---

## 📝 TODO (будущие улучшения)

1. **Оптимизация хранения:**
   - [ ] Сжатие координат (упрощение маршрута)
   - [ ] Автоматическая очистка старых маршрутов

2. **Android:**
   - [ ] Запрос полного маршрута после завершения забега
   - [ ] Отображение максимальной скорости соперника
   - [ ] Воспроизведение забега с анимацией

3. **Backend:**
   - [ ] Пагинация для endpoint `/route`
   - [ ] WebSocket уведомление о новых точках маршрута
   - [ ] Статистика по маршрутам (средняя скорость по участкам)

---

## 🐛 Известные ограничения

1. **Точки маршрута сохраняются только при наличии координат**
   - Если GPS недоступен, точка не сохранится
   - Решение: Android должен отправлять последние известные координаты

2. **Нет защиты от дублирования точек**
   - Если клиент отправит одну и ту же точку дважды, она сохранится дважды
   - Решение: Добавить unique constraint на (challenge_id, user_id, elapsed_time_millis)

3. **Race condition при одновременном завершении**
   - Если оба участника достигнут цели одновременно, возможна двойная обработка
   - Решение: Добавить блокировку на уровне БД или проверку статуса перед обновлением

---

## 📞 Поддержка

При возникновении проблем:
1. Проверьте логи сервера на наличие ошибок миграции
2. Убедитесь, что все новые поля созданы в БД
3. Проверьте версию Android клиента

---

**Автор:** Claude Code  
**Дата:** 2026-05-08
