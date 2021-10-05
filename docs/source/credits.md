# Credits

## Vision

The vision for this project: to create a first-class Python package of retry utilities of high enough quality to be included in the standard library, in the same way `attrs` became `dataclasses`. That led to the following goals:
- Fully type annotated, passing [mypy](https://mypy.readthedocs.io/en/stable/)'s static type checker with strict flags
- 100% test coverage
- Support for all modern versions of Python
- No external dependencies, i.e. stdlib only
- High-quality auto-generated documentation
- Full compatibility with `inspect`, coroutine functions, and [dunder](https://wiki.python.org/moin/DunderAlias) attributes

## Inspiration

### Custom logger

The Python package [`retry`](https://github.com/invl/retry) was the first place I looked when trying out retry utilities. Although it's since been abandoned, I appreciated the option to provide a custom logger.

### Async support

The Python package [`tenacity`](https://tenacity.readthedocs.io/en/latest/index.html) inspired me to support coroutine functions. While I don't prefer its verbose API, it has an impressive range of features I made sure to include in `tubthumper`.

### Jitter

Two articles by Marc Brooker — [Timeouts, retries, and backoff with jitter](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/) and [Exponential Backoff And Jitter](https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/) — introduced me to the benefits of randomly jittering backoff timing. Highly recommend!

## Contributors

`tubthumper` is written and maintained by Matt Fay.

A full list of contributors can be found on [GitHub](https://github.com/matteosox/tubthumper/graphs/contributors).

## License

`tubthumper` is licensed under the [Apache License 2.0](https://choosealicense.com/licenses/apache-2.0/), reproduced below:

```{literalinclude} ../../LICENSE
```
