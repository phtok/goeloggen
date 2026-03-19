.PHONY: help install-dev install-all dev-up dev-down api worker lint test smoke

help:
	@echo "Targets:"
	@echo "  install-dev Install editable package with dev deps"
	@echo "  install-all Install editable package with dev+vision+ml deps"
	@echo "  dev-up     Start postgres, redis, api and worker via docker compose"
	@echo "  dev-down   Stop docker compose stack"
	@echo "  api        Run API locally (expects dependencies installed)"
	@echo "  worker     Run worker locally (expects dependencies installed)"
	@echo "  lint       Run ruff (if installed)"
	@echo "  test       Run pytest (if installed)"
	@echo "  smoke      Python syntax smoke check"

install-dev:
	pip install -e ".[dev]"

install-all:
	pip install -e ".[dev,vision,ml]"

dev-up:
	cp -n .env.example .env || true
	docker compose up --build

dev-down:
	docker compose down

api:
	uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

worker:
	python -m app.worker.main

lint:
	ruff check app tests

test:
	pytest

smoke:
	python -m compileall app
