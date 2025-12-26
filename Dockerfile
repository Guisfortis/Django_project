FROM python:3.13.1

RUN apt-get update \
    && apt-get install -y \
        gcc \
        g++ \
        postgresql-client \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app


RUN pip install poetry
COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false &&\
poetry install --no-interaction --no-ansi --no-root






COPY hotel/ ./hotel/

WORKDIR /app/hotel

EXPOSE 8000


CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 127.0.0.1:8000"]