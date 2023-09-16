# Contributing to wasm_exec

Hi there! Thank you for even being interested in contributing to wasm_exec.
As an open source project, we are extremely open to contributions, whether they
be in the form of new features, improved infra, better documentation, or bug fixes.

## 🗺️ Guidelines

### 👩‍💻 Contributing Code

To contribute to this project, please follow a ["fork and pull request"](https://docs.github.com/en/get-started/quickstart/contributing-to-projects) workflow.
Please do not try to push directly to this repo unless you are maintainer.

Please follow the checked-in pull request template when opening pull requests. Note related issues and tag relevant
maintainers.

Pull requests cannot land without passing the formatting, linting and testing checks first. See
[Common Tasks](#-common-tasks) for how to run these checks locally.

It's essential that we maintain great documentation and testing. If you:
- Fix a bug
  - Add a relevant unit or integration test when possible. These live in `tests`.

### 🚩GitHub Issues

Our [issues](https://github.com/jflick58/wasm_exec/issues) page is kept up to date
with bugs, improvements, and feature requests.

If you start working on an issue, please assign it to yourself.

If you are adding an issue, please try to keep it focused on a single, modular bug/improvement/feature.
If two issues are related, or blocking, please link them rather than combining them.

We will try to keep these issues as up to date as possible, though
with the rapid rate of develop in this field some may get out of date.
If you notice this happening, please let us know.

### 🙋Getting Help

Our goal is to have the simplest developer setup possible. Should you experience any difficulty getting setup, please
contact a maintainer! Not only do we want to help get you unblocked, but we also want to make sure that the process is
smooth for future contributors.

In a similar vein, we do enforce certain linting, formatting, and documentation standards in the codebase.
If you are finding these difficult (or even just annoying) to work with, feel free to contact a maintainer for help -
we do not want these to get in the way of getting good code into the codebase.

## 🚀 Quick Start

This project uses [Poetry](https://python-poetry.org/) as a dependency manager. Check out Poetry's [documentation on how to install it](https://python-poetry.org/docs/#installation) on your system before proceeding.

❗Note: If you use `Conda` or `Pyenv` as your environment / package manager, avoid dependency conflicts by doing the following first:
1. *Before installing Poetry*, create and activate a new Conda env (e.g. `conda create -n langchain python=3.9`)
2. Install Poetry (see above)
3. Tell Poetry to use the virtualenv python environment (`poetry config virtualenvs.prefer-active-python true`)
4. Continue with the following steps.

To install requirements:

```bash
poetry install --all-extras
```

This will install all requirements for running the package, examples, linting, formatting, tests, and coverage. Note the `--all-extras` flag will install all optional dependencies necessary for integration testing.

❗Note: If you're running Poetry 1.4.1 and receive a `WheelFileValidationError` for `debugpy` during installation, you can try either downgrading to Poetry 1.4.0 or disabling "modern installation" (`poetry config installer.modern-installation false`) and re-install requirements. See [this `debugpy` issue](https://github.com/microsoft/debugpy/issues/1246) for more details.

Now, you should be able to run the common tasks in the following section. To double check, run `make test`, all tests should pass.

## ✅ Common Tasks

Type `make` for a list of common tasks.

### Code Formatting

Formatting for this project is done via a combination of [Black](https://black.readthedocs.io/en/stable/) and [isort](https://pycqa.github.io/isort/).

To run formatting for this project:

```bash
make format
```

### Linting

Linting for this project is done via a combination of [Black](https://black.readthedocs.io/en/stable/), [isort](https://pycqa.github.io/isort/), [flake8](https://flake8.pycqa.org/en/latest/), and [mypy](http://mypy-lang.org/).

To run linting for this project:

```bash
make lint
```

We recognize linting can be annoying - if you do not want to do it, please contact a project maintainer, and they can help you with it. We do not want this to be a blocker for good code getting contributed.

### Coverage

Code coverage (i.e. the amount of code that is covered by unit tests) helps identify areas of the code that are potentially more or less brittle.

To get a report of current coverage, run the following:

```bash
make coverage
```

### Testing

#### Unit Tests

Unit tests cover modular logic that does not require calls to outside APIs.

To run unit tests:

```bash
make test
```

If you add new logic, please add a unit test.

## Documentation

### Contribute Documentation

Right now, documentation is via docstrings and the README. In the future we will be adding
docs that are autogenerated by [sphinx](https://www.sphinx-doc.org/en/master/), so please follow
the sphinx docstring format.

<!-- # Docs are largely autogenerated by [sphinx](https://www.sphinx-doc.org/en/master/) from the code.

# For that reason, we ask that you add good documentation to all classes and methods.

# Similar to linting, we recognize documentation can be annoying. If you do not want to do it, please contact a project maintainer, and they can help you with it. We do not want this to be a blocker for good code getting contributed.

# ### Build Documentation Locally

# Before building the documentation, it is always a good idea to clean the build directory:

# ```bash
# make docs_clean
# ```

# Next, you can run the linkchecker to make sure all links are valid:

# ```bash
# make docs_linkcheck
# ```

# Finally, you can build the documentation as outlined below:

# ```bash
# make docs_build
# ``` -->

## 🏭 Release Process

As of now, wasm_exec has an ad hoc release process: releases are cut with high frequency by
a developer and published to [PyPI](https://pypi.org/project/langchain/).

wasm_exec follows the [semver](https://semver.org/) versioning standard. However, as pre-1.0 software,
even patch releases may contain [non-backwards-compatible changes](https://semver.org/#spec-item-4).
