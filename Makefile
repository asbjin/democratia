.PHONY: up down logs test etl seed migrate clean status

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

seed:
	docker compose --profile etl run --rm etl python scripts/seed_test_data.py

migrate:
	docker compose exec backend alembic upgrade head

status:
	docker compose ps

clean:
	docker compose down -v --remove-orphans
	rm -rf etl/data/*.zip etl/data/*.json
