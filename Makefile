fmt:
	@echo "Formatting files!"
	@echo "— Sorting imports with ISORT"
	@isort .
	@echo "— Formatting with BLACK"
	@black .

clean:
	@rm -rf `find . -name __pycache__`