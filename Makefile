.PHONY: clean build docs help
.DEFAULT_GOAL := help

define BROWSER_PYSCRIPT
import os, webbrowser, sys

try:
	from urllib import pathname2url
except:
	from urllib.request import pathname2url

webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

BROWSER := python -c "$$BROWSER_PYSCRIPT"

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

clean:  ## clean all build, python, and testing files
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +
	rm -fr .tox/
	rm -fr .coverage
	rm -fr coverage.xml
	rm -fr htmlcov/
	rm -fr .pytest_cache
	rm -fr layers
	rm -fr simulariumio-layer
	rm -f function.zip

build: ## run tox / run tests and lint
	tox

gen-docs: ## generate Sphinx HTML documentation, including API docs
	rm -f docs/simularium_lambdas*.rst
	rm -f docs/modules.rst
	sphinx-apidoc -o docs/ simularium_lambdas **/tests/
	$(MAKE) -C docs html

docs: ## generate Sphinx HTML documentation, including API docs, and serve to browser
	make gen-docs
	$(BROWSER) docs/_build/html/index.html

build-simulariumio-layer:
	make clean
	pip install simulariumio --target simulariumio-layer/python/lib/python3.8/site-packages
	pip install pint --target simulariumio-layer/python/lib/python3.8/site-packages
	rm -fr simulariumio-layer/python/lib/python3.8/site-packages/numpy simulariumio-layer/python/lib/python3.8/site-packages/numpy-*
	rm -fr simulariumio-layer/python/lib/python3.8/site-packages/pandas simulariumio-layer/python/lib/python3.8/site-packages/pandas-*
	mkdir layers
	cd simulariumio-layer && zip -r ../layers/simulariumio.zip .

publish-simulariumio-layer:
	aws lambda publish-layer-version --layer-name simulariumio --description "simulariumio"	--license-info "MIT" --zip-file fileb://layers/simulariumio.zip --compatible-runtimes python3.8 --cli-connect-timeout 6000

update-simulariumio-layer:
	make build-simulariumio-layer
	make publish-simulario-layer

## Run `make create-lambda function=xxx iam=xxx`
##    function: name of file containing the function (without extension) & name of Lambda function
##    iam     : your AWS IAM account ID
create-lambda: 
	make clean
	zip -rj function.zip scripts/$(function).py
	aws lambda create-function --function-name $(function) --zip-file fileb://function.zip --handler $(function).lambda_handler --runtime python3.8 --role arn:aws:iam::$(iam):role/lambda-ex

## Run `make invoke-lambda function=xxx`
invoke-lambda:
	aws lambda invoke --function-name $(function) out --log-type Tail --query 'LogResult' --output text |  base64 -d

## TODO: Add a update-layer-version or something like that, see https://docs.aws.amazon.com/lambda/latest/dg/invocation-layers.html