#!/usr/bin/env bash
set -e

# Run migrations
echo "🔄 Выполняем миграции..."

# Устанавливаем PYTHONPATH 
export PYTHONPATH="$(dirname "$(dirname "$0")")"

if alembic upgrade head; then
  echo "✅ Миграции выполнены успешно"
else
  echo "❌ Миграции не выполнены"
  exit 1
fi

# Запуск приложения
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
