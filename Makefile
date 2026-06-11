.PHONY: install up down seed chat test fmt lint typecheck

install:
	uv sync

up:
	docker compose up -d

down:
	docker compose down

seed:
	uv run python seed.py

chat:
	uv run python -m agent.chat

test:
	uv run pytest -v

fmt:
	uv run ruff format .
	uv run ruff check --fix .

lint:
	uv run ruff check .

typecheck:
	uv run mypy agent sql sources
