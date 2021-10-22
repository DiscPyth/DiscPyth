# Contributing to DiscPyth

I'm amazed that you want to contibute to this project, woah!
We love contributions `(that does include bug reports)` and here are certain things you can go through to make your contribution even better.

## Wanted contributions:
> - [x] Bug fixes in the code.
> - [x] Updating invalid links to documentaion.
> - [x] Released features/changes that are not documented.
> - [x] Fixing invalid/outdated example snippets in the documentation.
> - [x] Fixing of spelling, grammatical errors and incorrect statements or inaccuracies in the documentation.

## Unwanted contributions:
> - [ ] Removing whitespace.
> - [ ] Enhancements unrelated to the wrapper.
> - [ ] Modifications to the overall structure and format of the documentation.

> NOTE : Some contributions that are wanted or unwanted are (maybe) not mentioned here.

### Enhancing my reports:

Report a bug by [opening a new issue](https://github.com/DiscPyth/DiscPyth/issues),\
To get the best out of your bug reports you can follow these simple steps.

> NOTE : To be sure if its a bug or a mistake or just to be sure if your report is valid, you are recommended to ask for help on the [support server](https://discord.gg/8RATdNBs6n).

1. Properly describing your issue and what you  are trying to achive.
2. Providing the code causing the error with additional information on how you used it.
3. Providing your output logs.
4. Steps to reproduce
    - Be specific!
5. Notes (possibly including why you think this might be happening, or stuff you tried that didn't work)

### Contibution tips:

+ \* The code follows the [`black`](https://github.com/psf/black) formatting style, and so should you in your fixes. We also make use of [`isort`](https://github.com/pycqa/isort/) for sorting imports make sure to use it before opening a pull request!
    - To format your changes simply run the following
```bash
$ make fmt
```
+ `__pycache__`s are in `.gitignore` but you can addtionally run `$ make clean` to clean your directory.
+ If you are fixing whitespaces (it's an unwanted fix) you must either add it in a valid/wanted fix or completely ignore it.
+ Before modifing/enhancing the code structure you must discuss it first.
+ \* Follow the naming convention properly.
> \* Required when contributing. 

## Licence
By contributing, you agree that your contributions will be licensed under its MIT License.
