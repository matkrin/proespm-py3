default:
    just list

run:
    python src/proespm/main.py

test:
    rye test

build:
    rye run pyinstaller \
        --onefile \
        --noconsole \
        --name proespm \
        --add-data=src/proespm/templates:templates \
        src/proespm/main.py

clean:
    rm -r build/ dist/ *.spec
