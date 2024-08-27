.DEFAULT_GOAL := all

.PHONY: tests
tests:
	coverage run -m pytest --maxfail=1 -console_output_style=classic --junit-xml=.test-results.xml
	coverage report --precision=2 --show-missing --sort=Cover --skip-covered
	coverage lcov

.PHONY: html
html:
	coverage html --show-contexts
	open ./htmlcov/index.html

.PHONY: covpercent
covpercent:
	@coverage json
	@python -c "import json;print(round(float(json.load(open('coverage.json'))['totals']['percent_covered']),2))"

.PHONY: mypy
mypy:
	mypy --config-file pyproject.toml src/ tests/

.PHONY: lint
lint:
	ruff check --config ./pyproject.toml src/ tests/
	pylint --rcfile pyproject.toml src/ tests/

.PHONY: docs
docs:
	cd docs; jekyll build; jekyll serve --livereload; cd ..

all: mypy lint tests