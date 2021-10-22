fmt:
	@echo "Formatting files!"
	@echo "— Sorting imports with ISORT"
	@isort ./discpyth
	@echo "— Formatting with BLACK"
	@black ./discpyth

clean:
	@rm -rf `find . -name __pycache__`

check:
	@echo "Checking imports"
	@isort --check ./discpyth
	@echo "Checking formatting with BLACK"
	@black --check ./discpyth
	@echo "Running PyLint"
	@pylint ./discpyth
	@echo "Running Flake8"
	@flake8 ./discpyth
	@echo "Running MyPy"
	@mypy ./discpyth