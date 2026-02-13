# Installation

## Using prebuilt binaries

The easiest way to get started with `proespm` is by downloading a executable
binary for your operating system in the
[release section](https://github.com/matkrin/proespm-py3/releases/latest).

## Using uv

If you are comfortable with using Python from the command line, the best way is
using [uv](https://docs.astral.sh/uv/). It will automatically download all
required dependecies and a suitable Python interpreter when running the program
with

```sh
uv run src/proespm/main.py
```

from the project's root directory.

Furthermore, you can install the CLI with

```sh
uv tool install .
```

or

```sh
uv tool install --editable .
```

if you want to hack on it.

## Using pip

If you choose to use pip for installation, you have to make sure that you have
Python version 3.13 or higher installed. Then you can create a
[virtual environment](https://docs.python.org/3/library/venv.html) via

```sh
python3 -m venv .venv
```

and activate it with

```sh
. ./.venv/bin/activate
```

on UNIX-based systems. For other operating systems and more information about
virtual environments, see the
[official documentation](https://docs.python.org/3/library/venv.html).

Installation of the required dependecies is then done via

```sh
python3 -m pip install .
```

from the project's root.

Now you should be able to run `proespm` with

```sh
python3 src/proespm/main.py
```
