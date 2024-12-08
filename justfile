default:
    just list

run:
    uv run src/proespm/main.py

test:
    uv run pytest

build:
    uv run pyinstaller \
        --onefile \
        --noconsole \
        --name proespm \
        --add-data=src/proespm/templates:templates \
        src/proespm/main.py

clean:
    rm -r build/ dist/ *.spec
