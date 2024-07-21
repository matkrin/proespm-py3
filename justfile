default:
    just list

run:
    python src/prosurf/main.py

build:
    rye run pyinstaller \
        --onefile \
        --noconsole \
        --name proespm \
        --add-data=src/prosurf/templates:templates \
        src/prosurf/main.py

clean:
    rm -r build/ dist/ *.spec
