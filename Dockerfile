FROM python:3.10-alpine

WORKDIR /app

# Устанавливаем зависимости для PostgreSQL
RUN apk update && apk add --no-cache \
    postgresql-dev \
    gcc \
    musl-dev

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# Простая команда без миграций (миграции в docker-compose)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
