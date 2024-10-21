# Changelog

All notable changes for `tubthumper` will be documented in this file.
This project adheres to [Semantic Versioning](http://semver.org/) and [Keep a Changelog](http://keepachangelog.com/).

## 0.3.0 (2024-10-20)

### Added
- Tubthumper now supports Python 3.13

### Fixed
- Type annotation for `exceptions` argument of public interfaces now allows tuples of length greater than one exception.

### Deprecated
- Tubthumper no longer supports Python 3.8, which has reached its end of life.

## 0.2.0 (2024-01-08)

### Added
- Tubthumper now supports Python 3.12

### Deprecated
- Tubthumper no longer supports Python 3.7, which has reached its end of life.

## 0.1.0 (2022-12-05)

### Added
- Tubthumper now supports Python 3.11
- `typing_extensions` now installed for Python versions < 3.10
- Type annotations now use `typing.ParamSpec` to annotate types of decorated functions

### Changed
- Package version is now hardcoded instead of stored in a file.

### Deprecated
- Tubthumper no longer supports Python 3.6, which has reached its end of life.

## 0.0.1 (2022-06-17)

### Changed
- Reduced overhead of retry utilities by calculating backoff incrementally

## 0.0.0 (2021-10-16)

### Added
- `retry` function
- `retry_decorator` function
- `retry_factory` function
- `RetryError` exception
