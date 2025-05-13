FROM python:3.11-slim-bookworm

# Dépendances système pour MSSQL, Node.js, npm, etc.
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gnupg \
        curl \
        ca-certificates \
        build-essential \
        nodejs \
        npm && \
    curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && \
    ACCEPT_EULA=Y apt-get install -y --no-install-recommends \
        msodbcsql18 \
        unixodbc \
        unixodbc-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . .

# Build Tailwind via django-tailwind (remplace "theme" si ton app s'appelle autrement)
RUN python manage.py tailwind install
RUN python manage.py tailwind build

RUN python manage.py collectstatic --noinput

ENV DJANGO_SETTINGS_MODULE=NewIsAlwaysBetter.settings
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["gunicorn", "NewIsAlwaysBetter.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "6", "--timeout", "120"]