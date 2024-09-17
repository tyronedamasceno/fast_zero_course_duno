#!/bin/sh

poetry run alembic upgrade head

poetry run fastapi dev --host 0.0.0.0 fast_zero/app.py
