.PHONY: all test docs serve lint hooks down

DBT = docker compose run --rm dbt

all:
	docker compose up --build -d

test:
	$(DBT) python /work/dbt/scripts/run_pipeline.py --test-only

docs:
	$(DBT) dbt docs generate --static

serve:
	docker compose up -d docs

lint:
	$(DBT) sqlfluff lint models tests

hooks:
	pre-commit install

down:
	docker compose down
