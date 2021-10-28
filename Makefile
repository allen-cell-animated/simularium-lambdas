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
	rm -fr simulariumio-layer/python/lib/python3.8/site-packages/numpy simulariumio-layer/python/lib/python3.8/site-packages/numpy-*
	rm -fr simulariumio-layer/python/lib/python3.8/site-packages/pandas simulariumio-layer/python/lib/python3.8/site-packages/pandas-*
	mkdir layers
	cd simulariumio-layer && zip -r ../layers/simulariumio.zip .

publish-simulariumio-layer:
	aws lambda publish-layer-version --layer-name simulariumio --description "simulariumio"	--license-info "MIT" --zip-file fileb://layers/simulariumio.zip --compatible-runtimes python3.8 --cli-connect-timeout 6000

## Can also get layers associated with a function this way: aws lambda get-function-configuration --function-name my-function --query 'Layers[*].Arn' --output yaml
update-lambda-config:
	aws lambda update-function-configuration --function-name $(function) --layers arn:aws:lambda:us-west-2:420165488524:layer:AWSLambda-Python38-SciPy1x:29 arn:aws:lambda:us-west-2:770693421928:layer:Klayers-python38-pandas:38 $(simulariumio_arn)

## Run `make update-simulariumio-layer function=xxx`
## FIXME: line 84 doesn't get the latest version number after build and publish
update-simulariumio-layer:
	make build-simulariumio-layer
	make publish-simulariumio-layer
	make add-layers function=$(function)

## Run `make create-lambda function=xxx iam=xxx`
##    function: name of file containing the function (without extension) & name of Lambda function
##    iam     : your AWS IAM account ID
create-lambda: 
	make clean
	zip -rj function.zip scripts/$(function).py
	aws lambda create-function --function-name $(function) --zip-file fileb://function.zip --handler $(function).lambda_handler --runtime python3.8 --role arn:aws:iam::$(iam):role/lambda-ex
	make add-layers function=$(function)

## Run `make add-layers function=xxx`
add-layers:
	$(eval LAYER_ARN=$(shell aws lambda list-layer-versions --layer-name simulariumio --region us-west-2 --query 'max_by(LayerVersions, &Version).LayerVersionArn'))
	make update-lambda-config function=$(function) simulariumio_arn=$(LAYER_ARN) 

## Run `make invoke-lambda function=xxx`
invoke-lambda:
	aws lambda invoke --function-name $(function) out --log-type Tail --query 'LogResult' --output text |  base64 -d
