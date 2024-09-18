
.PHONY: install lint test docker-up docker-down

install:
	poetry install

lint:
	poetry run ruff check .
	poetry run ruff check . --fix

test:
	poetry run pytest -v

docker-up:
	docker-compose up --build

docker-down:
	docker-compose down -v
