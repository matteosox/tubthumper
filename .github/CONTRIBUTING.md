# Contributor Guide

## Getting started

We use Docker as a clean, reproducible development environment within which to build, test, generate docs, and so on. As long as you have a modern version of Docker, you should be able to run the full test suite using the `cicd/test.sh` shell script, discussed [below](#tests). That's it! Of course, running things natively isn't a supported/maintained thing.

## Tests

_TL;DR: Run `cicd/test.sh` to run the full suite of tests._

Running the test suite generates four test reports which are incorporated into the documentation:
- [Pylint](pylint)
- [Mypy](mypy)
- [Pytest](pytest)
- [Coverage](coverage)

### Version Check

_TL;DR: Run `test/version.sh` to confirm version is valid._

The `test/version.sh` shell script checks the current version, ensuring that it isn't identical to any versions from the `main` branch's history. When starting a new feature branch, you'll want to increment the version, likely by incrementing the `.devN` number, in order to pass this test.

### Requirements Check

_TL;DR: Run `test/requirements.sh` to confirm requirements are up-to-date._

As described [below](#requirements), we auto-generate the `requirements.txt` file used to pin Python dependencies in the Docker development environment. The `test/requirements.sh` shell script ensures that any changes to the files associated with updating requirements have been propagated to `requirements.txt`.

If this test is failing, see the [requirements](#requirements) section above to remedy the issue.

### Black Code Formatting

_TL;DR: Run `test/black.sh` to format your code._

We use [Black](https://black.readthedocs.io/en/stable/index.html) for code formatting. To format your code, run the `test/black.sh` shell script to get all your spaces in a row. Black configuration can be found in the `pyproject.toml` file at the root of the repo.

Black is setup to discover Python files recursively from the root of the repo, ignoring files and directories matching any `.gitignore` files. To add more Python files for formatting, edit `test/black.sh`.

### isort Import Ordering

_TL;DR: Run `test/isort.sh` to order your imports._

For import ordering, we use [isort](https://pycqa.github.io/isort/). To get imports ordered correctly, run the `test/isort.sh` shell script. isort configuration can be found in the `pyproject.toml` file at the root of the repo.

isort is setup to discover Python files recursively from the root of the repo, ignoring files and directories matching any `.gitignore` files. To add more Python files for import ordering, edit `test/isort.sh`.

### shfmt Shell Script Formatting

_TL;DR: Run `test/shfmt.sh -w` to format your shell scripts._

We use [shfmt](https://github.com/mvdan/sh) for shell script formatting. To format your shell scripts, run the `test/shfmt.sh -w` shell script to get all your spaces in a row. shfmt configuration can be found in the `.editorconfig` file at the root of the repo.

shfmt is setup to discover all shell script files recursively from the root of the repo. To add more shell scripts for formatting, edit `test/shfmt.sh`.

### Pylint Code Linting

_TL;DR: Run `test/pylint.sh` to lint your code._

We use [Pyint](https://pylint.pycqa.org/en/latest/) for Python linting (h/t Itamar Turner-Trauring from his site [pythonspeed](https://pythonspeed.com/articles/pylint/) for inspiration). To lint your code, run the `test/pylint.sh` shell script. In addition to showing any linting errors, it will also print out a report, which is also saved as `docs/source/_static/pylint.txt` so it can be incorporated in the documentation. Pylint configuration can be found in the `pylintrc` file at the root of the repo.

Pylint is setup to lint the `tubthumper` & `test/unit_tests` packages along with the `./*.py`, `docs/**/*.py`, & `publish/*.py` modules. To add more modules or packages for linting, edit `test/pylint.sh`.

### Shellcheck Shell Script Linting

_TL;DR: Run `test/shellcheck.sh` to lint your shell scripts._

We use [ShellCheck](https://www.shellcheck.net/) for shell script linting (h/t [Julia Evans](https://wizardzines.com/comics/shellcheck/) for introducing me to shellcheck). To lint your shell scripts, run the `test/shellcheck.sh` shell script (yes, I know). Shellcheck configuration can be found in the `.shellcheckrc` file at the root of the repo.

Shellcheck is setup to run on all files tracked by git that end `.sh`. This can be edited in `test/inner_shellcheck.sh`.

### Mypy Static Type Checking

_TL;DR: Run `test/mypy.sh` to type check your code._

We use [Mypy](https://mypy.readthedocs.io/en/stable/) for static type checking. To type check your code, run the `test/mypy.sh` shell script. In addition to printing any type checking errors, Mypy will also generate an html report, which can be found in `docs/source/_static/mypy/index.html`, where it's incorporated into the documentation.

Mypy will run faster on subsequent runs since Mypy caches its results in the Docker development environment. Mypy configuration can be found in the `pyproject.toml` file at the root of the repo.

Mypy is setup to run on the `tubthumper` package. To add more modules or packages for type checking, edit `test/mypy.sh`.

### Unit Tests

_TL;DR: Run `test/unit_tests.sh` to unit test your code quickly._

While we use [`unittest`](https://docs.python.org/3/library/unittest.html) to write unit tests, we use [`pytest`](https://docs.pytest.org/) for running them. To unit test your code, run the `test/unit_tests.sh` shell script. This will run unit tests in Python 3.9 only, without any coverage reporting overhead, which should only take about a second.

`pytest` is setup to discover tests in the `test/unit_tests` directory. All test files must match the pattern `test*.py`. `pytest` configuration can be found in the `pyproject.toml` file at the root of the repo. To add more directories for unit test discovery, edit the `testpaths` configuration option.

### Tox

_TL;DR: Run `test/tox.sh` to run the full suite of unit tests._

We use [`tox`](https://tox.readthedocs.io/en/latest/config.html) for unit testing across all supported versions of Python. To run the full unit test suite, run the `test/tox.sh` shell script.

If you haven't run this before, the script will initialize `tox`, creating each Python environment we unit test our code in. This step is skipped on subsequent runs, making it MUCH faster. `tox` configuration can be found in the `pyproject.toml` file at the root of the repo.

Tox is setup to run `pytest` for each supported version of Python.

#### Test Coverage

Tox is also setup to confirm 100% test coverage using [Coverage.py](https://coverage.readthedocs.io/en/coverage-5.5/). In addition to printing any coverage gaps from the full test suite, Coverage.py will also generate an html report, which can be found in `docs/source/_static/coverage/index.html`, where it's incorporated into the documentation.

Coverage.py configuration can be found in the `pyproject.toml` file at the root of the repo.

### Packaging Tests

_TL;DR: Run `test/packaging.sh` to test the package build._

We use [`build`](https://pypa-build.readthedocs.io/en/latest/) to build source distributions and wheels. We then use [`check-wheel-contents`](https://github.com/jwodder/check-wheel-contents) to test for common errors and mistakes found when building Python wheels. Finally, we use [`twine check`](https://twine.readthedocs.io/en/latest/#twine-check) to check whether or not `tubthumper`'s long description will render correctly on PyPI. To test the package build, run the `test/packaging.sh` shell script. While there is no configuration for `build` or `twine`, the configuration for `check-wheel-contents` can be found in the `pyproject.toml` file at the root of the repo.

### Documentation Tests

_TL;DR: Run `test/docs.sh` to test the documentation._

See [below](#documentation) for more info on the documentation build process. In addition to building the documentation, the `test/docs.sh` shell script uses Sphinx's [`doctest`](https://www.sphinx-doc.org/en/master/usage/extensions/doctest.html) builder to ensure the documented output of usage examples is accurate. Note that the `README.md` file's ` ```python` code sections are transformed into `{doctest}` directives by `docs/source/conf.py` during the documentation build process. This allows the `README.md` to render code with syntax highlighting on Github & PyPI while still ensuring accuracy using `doctest`.

## Documentation

_TL;DR: To build the documentation website, run `docs/build.sh`._

We use [Sphinx](https://www.sphinx-doc.org/en/master/index.html) for documentation site generation. To build the documentation website, run the `docs/build.sh` shell script. To view it, open `docs/build/html/index.html` in your browser.

Sphinx will only generate pages that have changed since your last build, but isn't perfect at this determination, so you may need to clear out your `docs/build` directory to start fresh. Sphinx configuration can be found in `docs/source/conf.py`.

Sphinx is setup to generate pages based on what it finds in the `toctree` directive in `docs/source/index.md`. To add new pages, add them to the table of contents with that directive.

### API Reference

The "API Reference" page is mostly auto-generated using the [`autodoc`](https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html), [`autosummary`](https://www.sphinx-doc.org/en/master/usage/extensions/autosummary.html), [`intersphinx`](https://www.sphinx-doc.org/en/master/usage/extensions/intersphinx.html), and [`linkcode`](https://www.sphinx-doc.org/en/master/usage/extensions/viewcode.html) Sphinx extensions. Classes, functions, decorators, and so on need to be added manually to the `docs/source/api.rst` file, but once included, the entries are auto-generated using type annotations and docstrings.

### Docstring Formatting

We use the [`napoleon`](https://www.sphinx-doc.org/en/master/usage/extensions/napoleon.html) Sphinx extension to enable docstring formats other than Sphinx's default, rather unreadable format. Instead, we use [Google's docstring standard](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings). Types and defaults should not be referenced in the docstring, instead included in annotations.

### Auto-generated Github Links

We use the [`linkcode`](https://www.sphinx-doc.org/en/master/usage/extensions/linkcode.html) Sphinx extension to add links to Github on the API Reference page. The code for mapping Python objects to links can be found in the `docs/linkcode.py` Python module.

### Changelog

We document changes in the `CHANGELOG.md` file. This project adheres to the [keep a changelog](https://keepachangelog.com/en/1.0.0/) standard. Before committing changes that impact users, make sure to document features added, changed, deprecated, removed, fixed, or security-related changes to the "## Unreleased" section.

### Test Reports Pages

We include the various reports generated by the test process in the documentation, as you can see at the table of contents under "Contibutor Guide". While the Pylint report is simply included as ReST with some minor filtering to get things to look right, the Mypy, Pytest, and Coverage reports are each displayed with an embedded iframe.

### Custom Badges

The Mypy and Pylint badges displayed in the `README.md` use [shields.io](https://shields.io/endpoint)'s endpoint feature, which relies on an endpoint to provide json data. They refer to [a Gist](https://gist.github.com/matteosox/bd79bbd912687bf44fac6b7887d18f14) to provide the data required for rendering each score.

### Publishing Documentation

We use [Read the Docs](https://docs.readthedocs.io/en/stable/index.html) for building and publishing `tubthumper`'s documentation. Its Github integration makes this process seamless. Read the Docs configuration can be found in the `.readthedocs.yaml` file at the root of the repo.

Because we include the various reports generated during the test process as part of the documentation — see [above](#test-reports-pages) for more info — we have to find a way to get those reports into the Read the Docs environment. In the `docs/source/conf.py` config file for Sphinx, we run the `download_reports()` function when running there, detected by the `READTHEDOCS` environment variable. That `download_reports()` function polls Github's REST API for artifacts that match the current git SHA, downloading the reports artifact once it's found.

While documentation for the `tubthumper` package is generated and hosted by Read the Docs, the documentation can be found at a custom domain: [tubthumper.mattefay.com](https://tubthumper.mattefay.com). You can read more about this [here](https://docs.readthedocs.io/en/stable/custom_domains.html).

## Publishing

### Determining the Version

`tubthumper` is versioned according to [PEP 440](https://www.python.org/dev/peps/pep-0440/). The type of final release (major, minor, or micro) should be determined by the types of unreleased changes in the changelog. Any "Removed" changes call for a major release (increment the major digit, minor and micro reset to 0). "Added" changes call for a minor release (increment the minor digit, micro set to 0). Otherwise, a "micro" release is called for (increment the micro digit only).

Final releases should also be accompanied by an update to the changelog, renaming the "## Unreleased" section to "## {version} (YYYY-MM-DD)"

### Public vs. Private Releases

`tubthumper` uses a concept of public vs. private releases. Final releases, along with alpha, beta, and release-candidate prereleases are considered public, and are published. Private releases, i.e. dev or post releases, are not published publicly.

### Publishing the Package to PyPI

We use [`build`](https://pypa-build.readthedocs.io/en/latest/) to build source distributions and wheels, which we publish to [PyPI](https://pypi.org/) using [`twine`](https://twine.readthedocs.io/en/latest/). This is all handled by the `publish/package.sh` shell script. Private releases are published to [TestPyPI](https://test.pypi.org/).

### Publishing a Tag to Github

The `publish/tag.py` Python script uses Github's [Create a release](https://docs.github.com/en/rest/reference/repos#create-a-release) REST API to publish a tag with release notes. It creates a tag using the current version of the package, and also collects up change information from the changelog. Private releases are published as a "draft". This ensures the scipt is still working while making it easy to view the resulting release notes without actually publishing a tag. As well, draft releases are not visible to the public.

## Development Environment

### Docker Container

The `docker/create_container.sh` shell script builds the local development environment (a Docker container) for you. Different workflows (e.g. running tests, building docs, updating requirements) will use the `docker/exec.sh` shell script to `docker exec` a command in the running container.

If you'd like to run your own commands in there, you can run `docker/exec.sh YOUR COMMANDS HERE`. Alternatively, run `docker/exec.sh` without any arguments to start an interactive bash terminal.

The container will stop itself if more than five minutes of inactivity goes by, but feel free to `docker stop` it before then; the `docker/exec.sh` shell script is smart enough to restart the container the next time you use it. As well, it will create the container for you it hasn't been created yet using the `docker/create_container.sh` shell script.

### Docker Image

The `docker/build_image.sh` shell script builds the Docker image upon which the local development environment is based: `matteosox/tubthumper-cicd`. In`docker/Dockerfile`, you can see that it installs both OS-level and Python dependencies in a Ubuntu base image, while also installing the `tubthumper` package in [editable mode](https://pip.pypa.io/en/stable/cli/pip_install/#install-editable).

While the image is versioned per commit, you generally shouldn't need to rebuild it unless there are changes to more infrastructural stuff (e.g. anything in the `requirements` or `docker` directories). Even so, this is generally quite fast because of a few caching tricks.

#### Python & Apt Package Caching

We use the `RUN --mount=type=cache` functionality of Docker BuildKit to cache apt packages stored in `/var/cache/apt` and Python packages stored in `~/.cache/pip`. This keeps your local machine from re-downloading new packages each time. h/t Itamar Turner-Trauring from his site [pythonspeed](https://pythonspeed.com/articles/docker-cache-pip-downloads/) for inspiration.

#### Docker Layer Caching

As well, we use the new `BUILDKIT_INLINE_CACHE` feature to cache our images using Docker Hub. This is configured in the `docker build` command, and is smart enough to only download the layers you need. h/t Itamar Turner-Trauring from his site [pythonspeed](https://pythonspeed.com/articles/speeding-up-docker-ci/) for inspiration.

#### Caching in Github Actions

While the first caching trick won't speed things up in Github Actions, in theory, the second should. In practice however, Docker layer caching in general (for example, even with a more traditional `docker pull` preceding the build step) seems to be intermittent there, likely due to differences between the build agents.

## Requirements

_TL;DR: Run `requirements/update.sh` to update requirements._

### Package Requirements

One stated design goal for `tubthumper` is to have no external dependencies, i.e. stdlib only. However, in order to support some modern Python features in older versions, we DO have a few conditional dependencies, which can be found in the `install_requires` section of `setup.cfg`.

### Test Requirements

In addition to conditional dependencies to run on older versions of Python, `tubthumper` also requires additional packages to run unit tests. These can be found in `requirements/test_requirements.txt`, an auto-generated file produced from `requirements/test_requirements.in`. These are separated from the general requirements to allow `tox` to install just these in the various virtual environments it creates. See [above](#tox) for more info on `tox`.

### Docs Requirements

Building the documentation for `tubthumper` requires additional packages. These can be found in `requirements/docs_requirements.txt`, an auto-generated file produced from `requirements/docs_requirements.in`. These are separated from the general requirements to allow Read the Docs to install them in their build process. See [above](#publishing-documentation) for more info on Read the Docs.

### Dev Requirements

There are two requirements files associated with the `matteosox/tubthumper-cicd` Docker image:
1) `requirements/requirements.in`
2) `requirements/requirements.txt`

The `.in` file is where we collect immediate dependencies, described in PyPI format (with versions pinned only as needed). The `.txt` file is generated by running the `requirements/update.sh` shell script, which uses `pip-compile`. While using [hashes](https://pip.pypa.io/en/stable/cli/pip_install/#hash-checking-mode) would be nice, different platforms, e.g. Apple M1's ARM vs Intel's x86, sometimes require different wheels with different hashes. This is true despite ensuring a consistent Linux OS in Docker sadly. In the spirit of enabling a diverse ecosystem of developers with different machines, I've kept hashing off.

This gives us both a flexible way to describe dependencies while still achieving reproducible builds. Inspired by [this](https://hynek.me/articles/python-app-deps-2018/) and [this](https://pythonspeed.com/articles/pipenv-docker/).

## Continuous Integration & Continuous Deployment

We use Github actions to run our CI/CD pipeline on every pull request. The configuration can be found in `.github/workflows/cicd.yaml`. That said, every step of every job can also be run locally.

### Main

This is the "main" job, which consists of running the test suite, pushing to docker hub, and publishing the package. Each step is described below.

#### Test

See [above](#tests) for more info on testing.

#### Github Actions Artifacts

We store an artifact containing the various test reports, making debugging failed runs easier, and allowing Read the Docs to include them in the generated documentation. You can read more about Github Actions' artifacts feature [here](https://docs.github.com/en/actions/advanced-guides/storing-workflow-data-as-artifacts).

To label the artifacts with the appropriate SHA, we have to do a bit of work, since Github Actions runs workflows triggered from a pull request with a "future commit", i.e. the resulting SHA (and code of course) from the proposed merge into the `main` branch. Specifically, the `ref` is `refs/pull/{PR_NUMBER}/merge`, which you can actually get the SHA of by running `git ls-remote` locally.

This is neat, but also complicates things, since workflows triggered from a push event behave as expected, i.e. the resulting SHA is the one pushed. To get around this, the previous step of the job determines the git SHA of the originating commit, taking into account this complication.

#### Push to Docker Hub

On workflows triggered from the `main` branch, the `matteosox/tubthumper-cicd` Docker image is pushed to Dockerhub using the `cicd/push_to_dockerhub.sh` shell script. Authentication is handled by the previous `docker/login-action@v1` build action, which uses login credentials stored as Github Actions secrets.

In addition to pushing the image tagged with the git SHA of the code producing it, it also pushes an untagged (i.e. tagged as `latest`) image.

#### Update Badge Data Gist

On workflows triggered from the `main` branch, the badge data Gist is updated using the `cicd/update_gist.sh` shell script, which uses the `GIST_TOKEN` secret to authenticate to Github's REST API. See [above](#custom-badges) for more info.

#### Publish

On workflows triggered from the `main` branch, the package is published using the `cicd/publish.sh` shell script. See [above](#publishing) for more info.

### OS Compatibility

We use [`tox-gh-actions`](https://opensourcelibs.com/lib/tox-gh-actions) to configure tox to run on multiple versions of Python in a separate job intended to test compatibility across different operating systems. Using Github Actions' [build matrix feature](https://docs.github.com/en/actions/learn-github-actions/managing-complex-workflows#using-a-build-matrix), we're able to run unit tests on MacOS, Windows, & Linux, for each supported version of Python.

#### Codecov

In addition to validating that test coverage is 100% as part of the "main" CI/CD workflow — discussed further in the [test coverage](#test-coverage) section — we also upload coverage reports to codecov.io. This provides nice pull request comments and annotation, in addition to a fancy badge. Codecov configuration can be found in the `codecov.yml` file at the root of the repo.

### Weekly

A separate `weekly` workflow is configured in `.github/workflows/weekly.yaml`. This workflow runs the non-publishing portions of the `main` workflow, except it explicitly builds the development Docker image from scratch, ensuring that the base image and any apt packages aren't ignored due to Docker layer cacheing. h/t Itamar Turner-Trauring from his site [pythonspeed](https://pythonspeed.com/articles/docker-cache-insecure-images/) for inspiration.

## Pull Requests

The `main` branch has [branch protections](https://help.github.com/en/github/administering-a-repository/about-protected-branches) turned on in Github, requiring one reviewer to approve a PR before merging. We also use the code owners feature to specify who can approve certain PRs. As well, merging a PR requires status checks (Read the Docs, both CI/CD jobs, and codecov) to complete successfully.

When naming a branch, please use the syntax `username/branch-name-here`. If you plan to collaborate with others on that branch, use `team/branch-name-here`.

## Future Work

-- Remove python3.10-distutils once pip migrates from `distutils` to `sysconfig`. See [here](https://pip.pypa.io/en/stable/news/#id60) & [here](https://docs.python.org/3.10/library/distutils.html#module-distutils).
- Update type annotations to use `types.ParamSpec` once Mypy supports them (currently a new feature in Python 3.10). See [here](https://github.com/python/mypy/issues/8645).
- Remove `-x` command-line argument from `inner_shellcheck.sh` once using version >= 0.8.0 (see [here](https://github.com/koalaman/shellcheck/blob/master/CHANGELOG.md#added)), and remove `disable=SC1090` (can't find non-constant source) once using version >= 0.7.2 (see [here](https://github.com/koalaman/shellcheck/blob/master/CHANGELOG.md#changed-1))
- Remove constraints in `requirements/test_requirements.in` when no longer supporting Python 3.6.
