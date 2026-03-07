default:
    just --list

run:
    uv run src/proespm/main.py

test:
    uv run pytest

lint:
    uv run ruff check

format:
    uv run ruff format

format-check:
    uv run ruff format --check

typecheck:
    uv run ty check src

build:
    uv run pyinstaller \
        --onefile \
        --noconsole \
        --name proespm \
        --add-data=src/proespm/templates:templates \
        src/proespm/main.py

clean:
    rm -r build/ dist/ *.spec

docs-serve:
    uv run mkdocs serve --watch ./docs --open

docs-build:
    uv run mkdocs build

testreport:
    uv run proespm ./tests/testdata
