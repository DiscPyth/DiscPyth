#!/usr/bin/env python3

import argparse
import sys

import pylint.lint as pylnt
from black import freeze_support, main, maybe_install_uvloop, patch_click
from flake8.main import cli as flk8
from isort.main import main as isort
from mypy.main import main as mypy

parser = argparse.ArgumentParser(
    description="Developmenr Utilities for DiscPyth."
)

subparser = parser.add_subparsers(dest="command")

check = subparser.add_parser("check")
check.add_argument(
    "-s",
    help="Specify checks to be skipped, 'i' for isort, 'b' for black, 'p' for pylint, 'f' for flake8 and 'm' for mypy. Separate by comma(,) ex '-s i, b, p, f'.",
)

fmt = subparser.add_parser("fmt")
fmt.add_argument(
    "-s",
    help="Specify formatting tools to be skipped, 'i' for isort, 'b' for black. Separate by comma(,) ex '-s i, b'.",
)

args = parser.parse_args()


def isrt():
    print("Checking imports with isort")
    isort(argv=["--check", "./discpyth"])


def f_isrt():
    print("Checking imports with isort")
    isort(argv=["./discpyth"])


def blk():
    print("Checking formatting with black")
    maybe_install_uvloop()
    freeze_support()
    patch_click()
    main(["--check", "./discpyth"])


def f_blk():
    print("Checking formatting with black")
    maybe_install_uvloop()
    freeze_support()
    patch_click()
    main(["./discpyth"])


def plnt():
    print("Running pylint")
    pylnt.Run(["./discpyth"])


def flk():
    print("Running flake8")
    flk8.main(["./discpyth"])


def mp():
    print("Checking typing with mypy")
    try:
        mypy(None, sys.stdout, sys.stderr, ["./discpyth"])
        sys.stdout.flush()
        sys.stderr.flush()
    except BrokenPipeError:
        # Python flushes standard streams on exit; redirect remaining output
        # to devnull to avoid another BrokenPipeError at shutdown
        devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(devnull, sys.stdout.fileno())
        sys.exit(2)


checkers = {
    "i": isrt,
    "b": blk,
    "p": plnt,
    "f": flk,
    "m": mp,
}

formatters = {"i": f_isrt, "b": f_blk}

if args.command == "check":
    todo = ["i", "b", "p", "f", "m"]
    if args.s:
        for t in args.s.split(","):
            todo.remove(t.strip())
        print(f"Performing checks with following skipped,\n{args.s}")
    else:
        print("Performing a full check.")
    for tool in todo:
        try:
            checkers[tool]()
        except SystemExit as e:
            if e.code != 0:
                print(f"An error occured while running {tool}.")
                raise
            else:
                pass
if args.command == "fmt":
    todo = ["i", "b"]
    if args.s:
        for t in args.s.split(","):
            todo.remove(t.strip())
        print(f"Formatting with following skipped,\n{args.s}")
    else:
        print("Formatting...")
    for tool in todo:
        try:
            formatters[tool]()
        except SystemExit as e:
            if e.code != 0:
                raise
            else:
                pass
