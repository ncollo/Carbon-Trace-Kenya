# Development helper Makefile

.PHONY: help install up down migrate test worker run

help:
	@echo "make install     # install python dependencies"
	@echo "make up          # start docker-compose services (postgres, redis, web, worker)"
	@echo "make down        # stop compose services"
	@echo "make migrate     # run alembic migrations"
	@echo "make test        # run pytest"
	@echo "make worker      # run worker locally"
	@echo "make run         # run uvicorn locally"

install:
	python -m pip install --upgrade pip
	pip install -r requirements.txt

up:
	docker-compose up -d --build

down:
	docker-compose down

migrate:
	# Ensure DATABASE_URL is set in environment (.env)
	alembic upgrade head

test:
	pytest -q

worker:
	python worker.py

run:
	uvicorn api.main:app --reload
