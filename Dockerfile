FROM python:3.12.3-slim

ENV POETRY_VIRTUALENVS_CREATE=false
RUN apt-get update && apt-get install -y --no-install-recommends gcc python3-dev

WORKDIR app/
COPY . .

RUN pip install poetry

RUN poetry config installer.max-workers 10
RUN poetry install --no-interaction --no-ansi

EXPOSE 8000
CMD poetry run fastapi run fast_zero/app.py
