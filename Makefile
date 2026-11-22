.PHONY: up down test lint seed psql

up:
	docker compose up -d --build

down:
	docker compose down

test:
	PYTHONPATH=backend pytest backend/tests -q

lint:
	ruff check backend

seed:
	@echo "seed hook arrives in P1"

psql:
	docker compose exec db psql -U cercos -d cercos
