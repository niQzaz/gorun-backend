-- Миграция для добавления таблицы точек маршрута совместных забегов
-- Дата: 2026-05-08

-- Создание таблицы для хранения точек маршрута
CREATE TABLE IF NOT EXISTS joint_run_challenge_route_points (
    id SERIAL PRIMARY KEY,
    challenge_id INTEGER NOT NULL REFERENCES joint_run_challenges(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    sequence_index INTEGER NOT NULL,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    elapsed_time_millis INTEGER NOT NULL,
    distance_meters DOUBLE PRECISION NOT NULL
);

-- Создание индексов для оптимизации запросов
CREATE INDEX IF NOT EXISTS joint_run_route_challenge_user_idx
    ON joint_run_challenge_route_points(challenge_id, user_id);

CREATE INDEX IF NOT EXISTS joint_run_route_sequence_idx
    ON joint_run_challenge_route_points(challenge_id, user_id, sequence_index);

-- Добавление полей для максимальной скорости участников
ALTER TABLE joint_run_challenges
    ADD COLUMN IF NOT EXISTS creator_max_speed_kmh DOUBLE PRECISION,
    ADD COLUMN IF NOT EXISTS opponent_max_speed_kmh DOUBLE PRECISION;

-- Комментарии к таблице и полям
COMMENT ON TABLE joint_run_challenge_route_points IS 'Точки маршрута участников совместных забегов';
COMMENT ON COLUMN joint_run_challenge_route_points.challenge_id IS 'ID совместного забега';
COMMENT ON COLUMN joint_run_challenge_route_points.user_id IS 'ID пользователя';
COMMENT ON COLUMN joint_run_challenge_route_points.sequence_index IS 'Порядковый номер точки в маршруте';
COMMENT ON COLUMN joint_run_challenge_route_points.latitude IS 'Широта';
COMMENT ON COLUMN joint_run_challenge_route_points.longitude IS 'Долгота';
COMMENT ON COLUMN joint_run_challenge_route_points.elapsed_time_millis IS 'Прошедшее время в миллисекундах';
COMMENT ON COLUMN joint_run_challenge_route_points.distance_meters IS 'Пройденная дистанция в метрах';
