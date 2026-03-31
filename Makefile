.PHONY: up down logs test etl migrate clean

up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f

test:
	docker compose exec backend python -m pytest tests/ -v
	cd frontend && npm test

etl:
	docker compose --profile etl run --rm etl python scripts/import_all.py

migrate:
	docker compose exec backend alembic upgrade head

clean:
	docker compose down -v --remove-orphans
	rm -rf etl/data/*.zip etl/data/*.json
