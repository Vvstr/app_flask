# Используем официальный Python образ
FROM python:3.10-slim AS base

# Рабочая директория
WORKDIR /app

# Устанавливаем зависимости
FROM base AS builder
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем приложение
FROM builder AS final
COPY . .

# Открываем порт
EXPOSE 5000

# Запускаем приложение
CMD ["python", "app.py"]
