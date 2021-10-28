# Simularium Lambdas

[![Build Status](https://github.com/allen-cell-animated/simularium_lambdas/workflows/Build%20Main/badge.svg)](https://github.com/allen-cell-animated/simularium_lambdas/actions)
[![Documentation](https://github.com/allen-cell-animated/simularium_lambdas/workflows/Documentation/badge.svg)](https://allen-cell-animated.github.io/simularium_lambdas/)
[![Code Coverage](https://codecov.io/gh/allen-cell-animated/simularium_lambdas/branch/main/graph/badge.svg)](https://codecov.io/gh/allen-cell-animated/simularium_lambdas)

AWS Lambdas for Simularium

---

## Dev Notes
- 9/8/2021
    - We added new Makefile scripts to carry out some routine AWS tasks via the command line (see "Commands You Need to Know" below).
    - We published the cellpack converter Lambda and verified that we can use it to convert CellPack data to a Simularium file through a REST API. The Lambda and the API configuration are under the aics-ac AWS account, in the region us-west-2. The API Gateway API is named cellpack-API.
    - In order to keep the simulariumio layer under the size limit, we had to remove numpy and Pandas from the simulariumio package and attach the SciPy and Pandas layers to the Lambda separately. Pandas layer ARN: `arn:aws:lambda:us-west-2:770693421928:layer:Klayers-python38-pandas:38`
    - We started to write a Lambda function for converting Readdy files but realized that the converter needs a filepath in a local operating system as an input, as do the other converters. We need to think more about the best way to handle this issue.

## Features

-   Store values and retain the prior value in memory
-   ... some other functionality

## Quick Start

```python
from simularium_lambdas import Example

a = Example()
a.get_value()  # 10
```

## Installation

**Stable Release:** `pip install simularium_lambdas`<br>
**Development Head:** `pip install git+https://github.com/allen-cell-animated/simularium_lambdas.git`

## Documentation

For full package documentation please visit [allen-cell-animated.github.io/simularium_lambdas](https://allen-cell-animated.github.io/simularium_lambdas).

## Development

See [CONTRIBUTING.md](CONTRIBUTING.md) for information related to developing the code.

## Commands You Need To Know

1. `pip install -e .[dev]`

    This will install your package in editable mode with all the required development
    dependencies (i.e. `tox`).

2. `make build`

    This will run `tox` which will run all your tests in both Python 3.7
    and Python 3.8 as well as linting your code.

3. `make clean`

    This will clean up various Python and build generated files so that you can ensure
    that you are working in a clean environment.

4. `make docs`

    This will generate and launch a web browser to view the most up-to-date
    documentation for your Python package.

5. `make update-simulariumio-layer function=xxx`

    This will prepare a new version of the simulariumio layer and publish it to AWS, automatically incrementing
    the published version number as well. Then, it will update the layer in the Lambda function named [function] to the latest version.

6. `make create-lambda function=xxx iam=xxx`
    
    This will create a new AWS Lambda named [function] from a file with the name [function] inside the
    scripts directory, given the AWS IAM account ID [iam].

4. `make add-layers function=xxx`

    This will add the SciPy, Pandas, and Simulariumio layers (the latest published version) to the Lambda function named [function].

7. `make invoke-lambda function=xxx`

    This will call an AWS Lambda function named [function] for testing.

#### Troubleshooting

- Lambda times out
    - Go to the Configuration tab in the Lambda page, then General configuration. You can edit the timeout there (max 15 minutes).
- 403 error when making POST request
    - Actually deploy the API endpoint


#### Additional Optional Setup Steps:

-   Turn your project into a GitHub repository:
    -   Make an account on [github.com](https://github.com)
    -   Go to [make a new repository](https://github.com/new)
    -   _Recommendations:_
        -   _It is strongly recommended to make the repository name the same as the Python
            package name_
        -   _A lot of the following optional steps are *free* if the repository is Public,
            plus open source is cool_
    -   After a GitHub repo has been created, run the commands listed under:
        "...or push an existing repository from the command line"
-   Register your project with Codecov:
    -   Make an account on [codecov.io](https://codecov.io)(Recommended to sign in with GitHub)
        everything else will be handled for you.
-   Ensure that you have set GitHub pages to build the `gh-pages` branch by selecting the
    `gh-pages` branch in the dropdown in the "GitHub Pages" section of the repository settings.
    ([Repo Settings](https://github.com/allen-cell-animated/simularium_lambdas/settings))
-   Register your project with PyPI:
    -   Make an account on [pypi.org](https://pypi.org)
    -   Go to your GitHub repository's settings and under the
        [Secrets tab](https://github.com/allen-cell-animated/simularium_lambdas/settings/secrets/actions),
        add a secret called `PYPI_TOKEN` with your password for your PyPI account.
        Don't worry, no one will see this password because it will be encrypted.
    -   Next time you push to the branch `main` after using `bump2version`, GitHub
        actions will build and deploy your Python package to PyPI.

#### Suggested Git Branch Strategy

1. `main` is for the most up-to-date development, very rarely should you directly
   commit to this branch. GitHub Actions will run on every push and on a CRON to this
   branch but still recommended to commit to your development branches and make pull
   requests to main. If you push a tagged commit with bumpversion, this will also release to PyPI.
2. Your day-to-day work should exist on branches separate from `main`. Even if it is
   just yourself working on the repository, make a PR from your working branch to `main`
   so that you can ensure your commits don't break the development head. GitHub Actions
   will run on every push to any branch or any pull request from any branch to any other
   branch.
3. It is recommended to use "Squash and Merge" commits when committing PR's. It makes
   each set of changes to `main` atomic and as a side effect naturally encourages small
   well defined PR's.


**MIT license**

