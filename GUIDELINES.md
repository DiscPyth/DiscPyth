# Contribution Guidelines

## Setting things up
--------------------

1. Step one is to set-up a proper development environment.
    - You are recommended to use `pipenv` for this task.
    - After setting up a virtual environment you may proceed with installing the dependencies.
        + i.e. `isort`, `black`, `pylint`, `flake8`, `mypy`
        + and... `wsproto`, `httpx`, `anyio`, `curio`.

2. If you are on a UNIX-like system:
    - You should make `dutils.py` "executable".
    - Run the following command `chmod +x ./dutils.py` (assuming you are in the root dir).

3. If you are on a Windows machine:
    - Then uh idk just use `py dutils.py [args here]`.
    - Or if you know a better solution with `.bat` or `.cmd` file or some windows magic, then create a PR.

## Some general points to note:
-------------------------------

- Unwanted changes such as whitespace fixing, can be included in a wanted change.

- You must always make use of `dutils.py fmt` and `dutils.py check`.

- The docstrings format is:

```py
"""
[ summary ]

# And optionally Attributes if its a
# class docstring or something

Attributes:
    `attribute_name (attribute_type)`: [ summary ]

Arguments:
    `argument_name (argument_type)`: [ summary ]

Keyword Arguments:
    `argument_name (argument_type)`: [ summary ]

    # If keyword arguments are defined with ** then

    `name_of_the_**_argument`:
        `names_of_possible_accepted_arguments (type_of_those_arguments)`: [ summary ]

Raises:
    `whatever_it_raises`: [ summary of "why?" ]

Returns:
    `whatever_it_returns`: [ some short summary ]
"""
```
