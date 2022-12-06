# Changelog

All notable changes for `tubthumper` will be documented in this file.
This project adheres to [Semantic Versioning](http://semver.org/) and [Keep a Changelog](http://keepachangelog.com/).

## Unreleased

### Added
- Tubthumper now supports Python 3.11
- `typing_extensions` now installed for Python versions < 3.10
- Type annotations now use `typing.ParamSpec` to annotate types of decorated functions

### Changed

### Deprecated
- Tubthumper no longer supports Python 3.6, which has reached its end of life.

### Removed

### Fixed

### Security

## 0.0.1 (2022-06-17)

### Changed
- Reduced overhead of retry utilities by calculating backoff incrementally

## 0.0.0 (2021-10-16)

### Added
- `retry` function
- `retry_decorator` function
- `retry_factory` function
- `RetryError` exception
