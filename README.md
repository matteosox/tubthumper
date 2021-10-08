<h1 align="center">
  <b>Tubthumper</b>: Helping you get up ... again!
</h1>

<p align="center">
  <a href="https://github.com/matteosox/tubthumper/actions/workflows/cicd.yaml">
    <img alt="CI/CD: n/a" src="https://github.com/matteosox/tubthumper/actions/workflows/cicd.yaml/badge.svg">
  </a>
  <a href="https://tubthumper.mattefay.com">
    <img alt="Docs: n/a" src="https://readthedocs.org/projects/tubthumper/badge/?version=latest">
  </a>
  <a href="https://pepy.tech/project/tubthumper">
    <img alt="Downloads: n/a" src="https://static.pepy.tech/personalized-badge/tubthumper?period=total&units=none&left_color=grey&right_color=blue&left_text=Downloads">
  </a>
  <a href="https://pypi.org/project/tubthumper/">
    <img alt="PyPI: n/a" src="https://img.shields.io/badge/dynamic/json?color=blueviolet&label=PyPI&query=%24.info.version&url=https%3A%2F%2Fpypi.org%2Fpypi%2Ftubthumper%2Fjson">
  </a>
  <a href="https://codecov.io/gh/matteosox/tubthumper">
    <img alt="codecov: n/a" src="https://codecov.io/gh/matteosox/tubthumper/branch/main/graph/badge.svg?token=8VKKDG9SMZ"/>
  </a>
  <a href="https://tubthumper.mattefay.com/en/latest/mypy.html">
    <img alt="MyPY: n/a" src="https://img.shields.io/endpoint?url=https%3A%2F%2Fgist.githubusercontent.com%2Fmatteosox%2Fbd79bbd912687bf44fac6b7887d18f14%2Fraw%2Fmypy.json"/>
  </a>
  <a href="https://tubthumper.mattefay.com/en/latest/pylint.html">
    <img alt="Pylint: n/a" src="https://img.shields.io/endpoint?url=https%3A%2F%2Fgist.githubusercontent.com%2Fmatteosox%2Fbd79bbd912687bf44fac6b7887d18f14%2Fraw%2Fpylint.json"/>
  </a>
</p>

----

## What's in a name?

**Tubthumper** is a Python package of retry utilities named after the English anarcho-communist rock band Chumbawamba's 1997 hit [Tubthumping](https://www.youtube.com/watch?v=2H5uWRjFsGc). Yes, really.

> I get knocked down, but I get up again. 🎶\
> You're never gonna keep me down. 🎶\
> I get knocked down, but I get up again. 🎶\
> You're never gonna keep me down... 🎶

## Getting Started

### Installation

`tubthumper` is a pip-installable package [hosted on PyPI](https://pypi.org/project/tubthumper/). Getting started is as easy as:

```shell
$ pip install tubthumper
```

### Usage

Import `tubthumper`'s useful bits:
```python
>>> from tubthumper import retry, retry_decorator, retry_factory
```

Call a function with retry and jittered exponential backoff:
```python
>>> retry(get_json, args=("spam",), exceptions=ConnectionError)
Function threw exception below on try 1, retrying in 0.157 seconds
Traceback (most recent call last):
...
ConnectionError: spam
{'some': ['json']}
```

Bake retry behavior into your function with a decorator:
```python
>>> @retry_decorator(exceptions=ConnectionError)
... def get_json(source):
...     return requests.get(f"https://{source}.org/json").json
>>> get_data("spam")
Function threw exception below on try 1, retrying in 0.546 seconds
Traceback (most recent call last):
...
ConnectionError: spam
{'some': ['json']}
```

Create a new function with retry behavior from an existing one:
```python
>>> get_json_retry = retry_factory(get_json, exceptions=ConnectionError)
>>> get_json_retry("spam")
Function threw exception below on try 1, retrying in 0.022 seconds
Traceback (most recent call last):
...
ConnectionError: spam
{'some': ['json']}
```

## Customization

While `tubthumper` ships with a set of sensible defaults, its retry behavior is fully customizable.

### Exceptions

Because overbroad except clauses are [the most diabolical python antipattern](https://realpython.com/the-most-diabolical-python-antipattern/), there is no sensible default for what exception or exceptions to catch and retry. Thus, every `tubthumper` interface has a required `exceptions` keyword-only argument, which takes an exception or tuple of exceptions to catch and retry on, i.e. a sensible lack of a default.

```python
>>> retry(get_json, args=("spam",), exceptions=ConnectionError)
Function threw exception below on try 1, retrying in 0.943 seconds
Traceback (most recent call last):
...
ConnectionError: spam
{'some': ['json']}
>>> retry(get_json, args=("spam",), exceptions=(KeyError, ConnectionError))
Function threw exception below on try 1, retrying in 0.054 seconds
Traceback (most recent call last):
...
ConnectionError: spam
{'some': ['json']}
```

By default, `tubthumper` raises a `tubthumper.RetryError` exception when all retries have been exhausted:

```python
>>> retry(get_json, args=("spam",), retry_limit=0, exceptions=ConnectionError)
Traceback (most recent call last):
...
tubthumper._retry_factory.RetryError: Retry limit 0 reached
```

You can override this behavior using the `reraise` flag to reraise the original exception in place of `RetryError`:

```python
>>> retry(get_json, args=("spam",), retry_limit=0, reraise=True, exceptions=ConnectionError)
Traceback (most recent call last):
...
ConnectionError: spam
```

### Retry Limits

By default, `tubthumper` will retry endlessly, but you have two means of limiting retry behavior. As shown previously, to limit the number of retries attempted, use the `retry_limit` keyword-only argument:

```python
>>> retry(get_json, args=("spam",), retry_limit=1, exceptions=ConnectionError)
Function threw exception below on try 1, retrying in 0.008 seconds
Traceback (most recent call last):
...
ConnectionError: spam
Traceback (most recent call last):
...
tubthumper._retry_factory.RetryError: Retry limit 1 reached
```

Alternatively, you can use the `time_limit` keyword-only argument (int or float) to set a time limit for the maximum number of seconds after the function is initially called for a retry attempt to begin:

```python
>>> retry(get_json, args=("spam",), time_limit=0.5, exceptions=ConnectionError)
Function threw exception below on try 1, retrying in 0.594 seconds
Traceback (most recent call last):
...
ConnectionError: spam
Traceback (most recent call last):
...
tubthumper._retry_factory.RetryError: Time limit 0.5 exceeded
```

### Backoff timing

The default backoff timing is to double the waiting period with each retry, starting off at one second, with each backoff period jittered, i.e. scaled by a uniformly distributed random number on the [0.0, 1.0) interval. You can disable jittering using the `jitter` keyword-only argument:

```python
>>> retry(get_json, args=("spam",), jitter=False, exceptions=ConnectionError)
Function threw exception below on try 1, retrying in 1 seconds
Traceback (most recent call last):
...
ConnectionError: spam
...
```

You can set the initial backoff period using the `init_backoff` keyword-only argument:

```python
>>> retry(get_json, args=("spam",), jitter=False, init_backoff=10, exceptions=ConnectionError)
Function threw exception below on try 1, retrying in 10 seconds
Traceback (most recent call last):
...
ConnectionError: spam
...
```

Finally, you can set the factor by which each successive backoff period is scaled using the `exponential` keyword-only argument:

```python
>>> retry(get_json, args=("spam",), jitter=False, exponential=10, exceptions=ConnectionError)
Function threw exception below on try 1, retrying in 1 seconds
Traceback (most recent call last):
...
ConnectionError: spam
Function threw exception below on try 2, retrying in 10 seconds
Traceback (most recent call last):
...
ConnectionError: spam
...
```

### Logging

By default, `tubthumper` logs each caught exception at the `logging.WARNING` level using a logger named `tubthumper`, i.e. `logging.getLogger("tubthumper")`. As described in the [Python logging tutorial](https://docs.python.org/3/howto/logging.html#configuring-logging-for-a-library), for this default logger, "events of severity WARNING and greater will be printed to sys.stderr" if no further logging is configured.

You can set the logging level using the `log_level` keyword-only argument:

```python
>>> retry(get_json, args=("spam",), log_level=logging.DEBUG, exceptions=ConnectionError)  # Nothing printed
...
```

You can provide your own logger using the `logger` keyword-only argument. This logger's `log` method will be called like so:

```python
logger.log(log_level, "Function threw...", exc_info=True)
```

## Features

### Compatible with methods

`tubthumper`'s various interfaces are compatible with methods, including classmethods and staticmethods:

```python
>>> class MyClass:
...     @retry_decorator(exceptions=ConnectionError)
...     def get_json(self, source):
...         return requests.get(f"https://{source}.org/json").json
...
>>> MyClass().get_json("spam")
Function threw exception below on try 1, retrying in 0.887 seconds
Traceback (most recent call last):
...
ConnectionError: spam
{'some': ['json']}
```

### Signature preserving

`tubthumper`'s various interfaces preserve the relevant [dunder](https://wiki.python.org/moin/DunderAlias) attributes of your function:

```python
>>> @retry_decorator(exceptions=ConnectionError)
... def func(one: bool, two: float = 3.0) -> complex:
...     """This is a docstring"""
...
>>> func.__name__
'func'
>>> func.__qualname__
'func'
>>> func.__module__
'__main__'
>>> func.__doc__
'This is a docstring'
>>> func.__annotations__
{'one': <class 'bool'>, 'two': <class 'float'>, 'return': <class 'complex'>}
```

`tubthumper` also preserves the inspect module's function signature, and `is*` functions:

```python
>>> import inspect
>>> inspect.signature(func)
<Signature (one: bool, two: float = 3.0) -> complex>
>>> inspect.isfunction(func)
True
>>> inspect.isroutine(func)
True
>>> inspect.ismethod(MyClass().get_json)
True
```

### Async support

`tubthumper`'s various interfaces support coroutine functions, awaiting them while using `async.sleep` between awaits:

```python
>>> @retry_decorator(exceptions=ConnectionError)
... async def get_json(source):
...     return await requests.async.get(f"https://{source}.org/json").json
...
>>> inspect.iscoroutinefunction(get_json)
True
```

### Fully type annotated

`tubthumper`'s various interfaces are fully type annotated, passing [mypy](https://mypy.readthedocs.io/en/stable/)'s static type checker:

```python
>>> retry_decorator.__annotations__
{
  'exceptions': typing.Union[typing.Type[Exception], typing.Tuple[typing.Type[Exception]]],
  'exponential': typing.Union[int, float],
  'init_backoff': typing.Union[int, float],
  'jitter': <class 'bool'>,
  'log_level': <class 'int'>,
  'logger': <class 'tubthumper._types.LoggerType'>,
  'reraise': <class 'bool'>,
  'retry_limit': typing.Union[int, float],
  'return': typing.Callable[[typing.Callable[..., ~ReturnType]], typing.Callable[..., ~ReturnType]],
  'time_limit': typing.Union[int, float]
}
```
