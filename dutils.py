#!/usr/bin/env python3

import argparse
import os
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
    help="Specify checks to be skipped, 'i' for isort, 'b' for black, 'p' for pylint, 'f' for flake8 and 'm' for mypy. Separate by comma(,) ex '-s i,b,p,f'.",
)
check.add_argument(
    "-i",
    action="store_true",
    help="If specified, tests will continue on error! (NOT RECOMMENDED)",
)

fmt = subparser.add_parser("fmt")
fmt.add_argument(
    "-s",
    help="Specify formatting tools to be skipped, 'i' for isort, 'b' for black. Separate by comma(,) ex '-s i,b'.",
)
fmt.add_argument(
    "-d",
    action="store_true",
    help="Print out the diff instead of formatting the files.",
)

args = parser.parse_args()


def isrt():
    print("Checking imports with isort")
    isort(argv=["--check", "./discpyth"])


def f_isrt(diff=False):
    print("Checking imports with isort")
    iargs = ["./discpyth"]
    iargs.append(  # pylint: disable=expression-not-assigned
        "--diff"
    ) if diff else None
    isort(argv=iargs)


def blk():
    print("Checking formatting with black")
    maybe_install_uvloop()
    freeze_support()
    patch_click()
    main(["--check", "./discpyth"])  # pylint: disable=no-value-for-parameter


def f_blk(diff=False):
    print("Checking formatting with black")
    maybe_install_uvloop()
    freeze_support()
    patch_click()
    bargs = ["./discpyth"]
    bargs.append(  # pylint: disable=expression-not-assigned
        "--diff"
    ) if diff else None
    main(bargs)  # pylint: disable=no-value-for-parameter


def plnt():
    print("Running pylint")
    pylnt.Run(["./discpyth"])


def flk():
    print("Running flake8")
    flk8.main(["./discpyth"])


def mypy_():
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
    "m": mypy_,
}

names = {
    "i": "isort",
    "b": "black",
    "p": "pylint",
    "f": "flake8",
    "m": "mypy",
}

formatters = {"i": f_isrt, "b": f_blk}

if args.command == "check":
    todo = ["i", "b", "p", "f", "m"]
    skp = []
    EXIT_CODE = 0
    if args.s:
        for t in args.s.split(","):
            try:
                tn = names[t]
            except KeyError:
                print(f"\u001b[38;5;9m[ ERROR ] No tool named {t}\u001b[0m")
            else:
                if t not in todo:
                    todo.remove(t)
                    skp.append(tn)
        if len(skp) == 0:
            print("Performing a full check.")
        else:
            print(
                f"Performing checks with following skipped,\n{', '.join(skp)}"
            )
    else:
        print("Performing a full check.")
    if args.i:
        print(
            "\u001b[38;5;208m[ WARNING ] Ignore mode is enabled, output logs may be hard to read\u001b[0m"
        )
    for idx, tool in enumerate(todo):
        try:
            checkers[tool]()
        except SystemExit as e:
            if e.code != 0:
                if not args.i:
                    print(f"An error occured while running {names[tool]}.")
                    raise
                if not idx == len(todo) - 1:
                    print(
                        f"An error occured while running {names[tool]}, ignoring..."
                    )
                EXIT_CODE = e.code
    if args.i:
        sys.exit(EXIT_CODE)
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
            formatters[tool](True if args.d else False)
        except SystemExit as e:
            if e.code != 0:
                raise
