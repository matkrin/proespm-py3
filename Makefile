test:
	poetry run pytest
typecheck:
	poetry run mypy -p vamas
typecheck-all:
	poertry run mypy .
format-check:
	poetry run black --check .
format:
	poetry run black .
