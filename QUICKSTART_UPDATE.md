# Быстрый старт - Обновление совместных пробежек

## 🚀 Что исправлено

1. ✅ Полные маршруты участников теперь сохраняются
2. ✅ Корректное определение победителя (с учетом времени при равных дистанциях)
3. ✅ Максимальная скорость участников передается через API
4. ✅ Новый endpoint для получения полных маршрутов

## 📋 Чек-лист обновления

### Backend (обязательно)
- [x] Создана таблица `joint_run_challenge_route_points`
- [x] Добавлены поля `creator_max_speed_kmh`, `opponent_max_speed_kmh`
- [x] Модифицирован endpoint `/joint-runs/{challenge_id}/live`
- [x] Добавлен endpoint `/joint-runs/{challenge_id}/route`
- [x] Исправлена логика определения победителя

### Запуск Backend
```bash
cd C:\Users\Amir\Downloads\app
python -m uvicorn app.main:app --reload
```

Миграции применятся автоматически при первом запуске.

### Android (требуется обновление)

**Критические изменения:**

1. **Добавить `maxSpeedKmh` в live updates:**
```java
// В RunFragment.java, метод sendJointRunLiveUpdate()
chatRepository.updateJointRunLive(
    jointRunId,
    currentLocation.getLatitude(),
    currentLocation.getLongitude(),
    totalDistanceMeters,
    elapsedTime,
    maxSpeedKmH,  // ← Добавить этот параметр
    callback
);
```

2. **Обновить модели:**
   - `JointRunLiveUpdateRequest.java` - добавить поле `maxSpeedKmh`
   - `ChatJointRun.java` - добавить поля `creatorMaxSpeedKmh`, `opponentMaxSpeedKmh`

3. **Добавить API метод:**
```java
// В ChatApi.java
@GET("chat/joint-runs/{challenge_id}/route")
Call<JointRunRouteResponse> getJointRunRoute(@Path("challenge_id") int challengeId);
```

## ✅ Проверка работоспособности

### 1. Проверить создание таблицы
```sql
SELECT COUNT(*) FROM joint_run_challenge_route_points;
```

### 2. Тест live update
```bash
curl -X POST http://localhost:8000/chat/joint-runs/1/live \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "latitude": 55.7558,
    "longitude": 37.6173,
    "distance_meters": 1500,
    "duration_millis": 300000,
    "max_speed_kmh": 12.5
  }'
```

### 3. Проверить сохранение точек
```sql
SELECT challenge_id, user_id, COUNT(*) as points_count
FROM joint_run_challenge_route_points
GROUP BY challenge_id, user_id;
```

### 4. Получить маршрут
```bash
curl http://localhost:8000/chat/joint-runs/1/route \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 🎯 Что дальше?

После обновления Android клиента:
1. Протестировать совместный забег от начала до конца
2. Проверить, что маршруты обоих участников сохраняются
3. Убедиться, что максимальная скорость отображается корректно
4. Проверить определение победителя в разных сценариях

## 📚 Подробная документация

См. `CHANGELOG_JOINT_RUN_FIXES.md` для полного описания изменений.

---

**Важно:** Backend обратно совместим со старыми Android клиентами, но для полной функциональности требуется обновление Android приложения.
