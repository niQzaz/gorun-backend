# Руководство по логированию | Logging Guide

## Обзор | Overview

Проект GoRun использует систему двуязычного логирования (русский/английский) для отслеживания всех операций в приложении.

The GoRun project uses a bilingual logging system (Russian/English) to track all application operations.

## Структура логов | Log Structure

### Модули логирования | Logging Modules

- `gorun.app` - Основное приложение | Main application
- `gorun.auth` - Авторизация и регистрация | Authentication and registration
- `gorun.chat` - Чат и сообщения | Chat and messages
- `gorun.friend` - Система друзей | Friends system
- `gorun.run` - Забеги пользователей | User runs
- `gorun.db` - База данных | Database
- `gorun.websocket` - WebSocket соединения | WebSocket connections

### Уровни логирования | Log Levels

- **DEBUG** - Детальная информация для отладки | Detailed debugging information
- **INFO** - Общая информация о работе | General operational information
- **WARNING** - Предупреждения о потенциальных проблемах | Warnings about potential issues
- **ERROR** - Ошибки, требующие внимания | Errors requiring attention

## Расположение логов | Log Location

Логи сохраняются в директории `app/logs/` с именем файла `gorun_YYYYMMDD.log`

Logs are saved in the `app/logs/` directory with filename `gorun_YYYYMMDD.log`

## Примеры логов | Log Examples

### Авторизация | Authentication

```
2026-05-09 03:20:15 | INFO     | gorun.auth | Попытка входа | Login attempt: username=john_doe
2026-05-09 03:20:15 | INFO     | gorun.auth | Успешный вход | Successful login: user_id=42, username=john_doe
2026-05-09 03:20:16 | WARNING  | gorun.auth | Вход отклонен: неверный пароль | Login rejected: invalid password - username=jane_doe, user_id=15
```

### Система друзей | Friends System

```
2026-05-09 03:21:30 | INFO     | gorun.friend | Отправка заявки в друзья | Sending friend request: from_user_id=42 to_user_id=15
2026-05-09 03:21:31 | INFO     | gorun.friend | Заявка в друзья успешно отправлена | Friend request sent successfully: request_id=123, from=42, to=15
2026-05-09 03:22:10 | INFO     | gorun.friend | Принятие заявки в друзья | Accepting friend request: request_id=123, user_id=15
```

### Забеги | Runs

```
2026-05-09 03:25:00 | INFO     | gorun.run | Создание забега | Creating run: user_id=42, name=Morning Run
2026-05-09 03:25:00 | DEBUG    | gorun.run | Добавление точек маршрута | Adding route points: run_id=567, points_count=150
2026-05-09 03:25:01 | INFO     | gorun.run | Забег успешно создан | Run successfully created: run_id=567, user_id=42, distance=5.2km
```

### Чат и сообщения | Chat and Messages

```
2026-05-09 03:26:00 | INFO     | gorun.chat | Начало чата | Starting chat: from_user_id=42, to_user_id=15
2026-05-09 03:26:05 | INFO     | gorun.chat | Отправка сообщения | Sending message: conversation_id=89, user_id=42, type=text
2026-05-09 03:26:05 | INFO     | gorun.chat | Сообщение создано | Message created: message_id=1001, type=text
```

### Совместные забеги | Joint Runs

```
2026-05-09 03:27:00 | INFO     | gorun.chat | Создание совместного забега | Creating joint run: conversation_id=89, creator_id=42, mode=distance
2026-05-09 03:27:00 | INFO     | gorun.chat | Совместный забег создан | Joint run created: challenge_id=25, creator=42, opponent=15
2026-05-09 03:27:30 | INFO     | gorun.chat | Принятие совместного забега | Accepting joint run: challenge_id=25, user_id=15
2026-05-09 03:28:00 | INFO     | gorun.chat | Оба участника готовы, забег начинается | Both ready, run starting: challenge_id=25
2026-05-09 03:35:00 | INFO     | gorun.chat | Забег завершен | Run finished: challenge_id=25, winner_id=42
```

### База данных | Database

```
2026-05-09 03:20:00 | INFO     | gorun.db | Запуск runtime миграций | Running runtime migrations
2026-05-09 03:20:00 | INFO     | gorun.db | Применение 3 миграций | Applying 3 migrations
2026-05-09 03:20:01 | INFO     | gorun.db | Runtime миграции успешно применены | Runtime migrations completed successfully
```

## Использование в коде | Usage in Code

### Импорт логгера | Import Logger

```python
from app.logger import auth_logger, chat_logger, run_logger, friend_logger
```

### Примеры использования | Usage Examples

```python
# INFO - успешные операции | successful operations
auth_logger.info(f"Успешный вход | Successful login: user_id={user.id}")

# DEBUG - детальная информация | detailed information
run_logger.debug(f"Добавление точек маршрута | Adding route points: count={len(points)}")

# WARNING - предупреждения | warnings
friend_logger.warning(f"Заявка отклонена | Request rejected: reason=already_exists")

# ERROR - ошибки | errors
chat_logger.error(f"Ошибка при сохранении | Error saving: {str(e)}")
```

## Мониторинг логов | Log Monitoring

### Просмотр логов в реальном времени | Real-time Log Viewing

```bash
# Windows PowerShell
Get-Content app\logs\gorun_20260509.log -Wait -Tail 50

# Linux/Mac
tail -f app/logs/gorun_20260509.log
```

### Поиск по логам | Search Logs

```bash
# Поиск ошибок | Search for errors
grep "ERROR" app/logs/gorun_20260509.log

# Поиск по пользователю | Search by user
grep "user_id=42" app/logs/gorun_20260509.log

# Поиск по модулю | Search by module
grep "gorun.auth" app/logs/gorun_20260509.log
```

## Рекомендации | Best Practices

1. **Используйте INFO** для важных операций (вход, создание, удаление)
   **Use INFO** for important operations (login, create, delete)

2. **Используйте DEBUG** для детальной отладки (промежуточные шаги)
   **Use DEBUG** for detailed debugging (intermediate steps)

3. **Используйте WARNING** для потенциальных проблем (отклоненные запросы)
   **Use WARNING** for potential issues (rejected requests)

4. **Используйте ERROR** для критических ошибок (исключения, сбои)
   **Use ERROR** for critical errors (exceptions, failures)

5. **Всегда включайте контекст**: user_id, conversation_id, run_id и т.д.
   **Always include context**: user_id, conversation_id, run_id, etc.

6. **Формат сообщений**: "Русский текст | English text: key=value"
   **Message format**: "Russian text | English text: key=value"
