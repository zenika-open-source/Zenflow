.PHONY: dev sync test

sync:
	uv sync --extra api --extra dev

dev: sync
	uv run zenflow-api

test: sync
	uv run pytest
