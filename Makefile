test:
	poetry run pytest
typecheck:
	poetry run mypy -p proespm-py3
typecheck-all:
	poertry run mypy .
format-check:
	poetry run black --check .
format:
	poetry run black .

.PHONY: build
build:
	poetry run pyinstaller --onefile --name proespm --add-data=proespm_py3/templates:templates -- pyinstaller_main.py
