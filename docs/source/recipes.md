# Recipes

```{testsetup}
from requests import ConnectionError

from tubthumper import retry, retry_decorator, retry_factory

URL = "http://ip.jsontest.com"
JSON = {"ip": "8.8.8.8"}


def get_ip(arg=[0]):
    arg[0] += 1
    if arg[0] % 3:
        raise ConnectionError(URL)
    return JSON

```

## Instantaneous Retries

Feeling impatient, but still want the logging benefits of `tubthumper`? Set `init_backoff=0`:

```{doctest}
>>> retry(get_ip, init_backoff=0, exceptions=ConnectionError)
WARNING: Function threw exception below on try 1, retrying in 0 seconds
Traceback (most recent call last):
  ...
requests.exceptions.ConnectionError: http://ip.jsontest.com
WARNING: Function threw exception below on try 2, retrying in 0 seconds
Traceback (most recent call last):
  ...
requests.exceptions.ConnectionError: http://ip.jsontest.com
{'ip': '8.8.8.8'}
```

## Constant Backoff

Not a believer in exponential, jittered backoff, but still want a constant backoff duration? Set `exponential=1` and `jitter=False`:

```{doctest}
>>> retry(get_ip, jitter=False, exponential=1, exceptions=ConnectionError)
WARNING: Function threw exception below on try 1, retrying in 1 seconds
Traceback (most recent call last):
  ...
requests.exceptions.ConnectionError: http://ip.jsontest.com
WARNING: Function threw exception below on try 2, retrying in 1 seconds
Traceback (most recent call last):
  ...
requests.exceptions.ConnectionError: http://ip.jsontest.com
{'ip': '8.8.8.8'}
```

## Retry Web Requests

Want to retry web requests selectively, e.g. server-side HTTP errors? Wrap `requests.request` with the `retry_decorator`:

```python
@retry_decorator(
    exceptions=(requests.HTTPError)
)
def request_with_retry(
    method: str, url: str, **kwargs: Any
) -> requests.models.Response:
    """
    Wrapper function for `requests.request` that retries
    server-side http errors with exponential backoff and jitter.
    For more info:
    https://docs.python-requests.org/en/latest/api/#requests.request
    """
    response = requests.request(method, url, **kwargs)
    if 500 <= response.status_code < 600:
        response.raise_for_status()
    return response
```

## Retrying a Generator Function

Retrying a generator has surprising results:

```{doctest}
>>> @retry_decorator(exceptions=ConnectionError)
... def gen_func():
...     response = get_ip()
...     for val in response["ip"].split('.'):
...         yield val
...
>>> for thing in gen_func():
...     print(thing)
...
Traceback (most recent call last):
  ...
requests.exceptions.ConnectionError: http://ip.jsontest.com
```

This is because, when a generator function is called, instead of executing the function, Python pauses it, returning a generator object:

```{doctest}
>>> gen_func()
<generator object gen_func at 0x...>
```

To retry the guts of a generator function, you'll want to put the retry inside:

```{doctest}
>>> def gen_func():
...     response = retry(get_ip, exceptions=ConnectionError)
...     for val in response["ip"].split('.'):
...         yield val
...
>>> for thing in gen_func():
...     print(thing)
...
WARNING: Function threw exception below on try 1, retrying in 0.420572 seconds
Traceback (most recent call last):
  ...
requests.exceptions.ConnectionError: http://ip.jsontest.com
8
8
8
8
```

## Retrying a property, staticmethod, or classmethod

Retrying a method is simple enough, but what about fancier object-oriented code? The `@retry_decorator` goes on the inside:

```{doctest}
>>> class Class:
...     @classmethod
...     @retry_decorator(exceptions=ConnectionError)
...     def cls_meth(self):
...         return get_ip()
...
...     @staticmethod
...     @retry_decorator(exceptions=ConnectionError)
...     def stat_meth():
...         return get_ip()
...
...     @property
...     @retry_decorator(exceptions=ConnectionError)
...     def prop(cls):
...         return get_ip()
...
>>> Class.cls_meth()
WARNING: Function threw exception below on try 1, retrying in 0.258917 seconds
Traceback (most recent call last):
  ...
requests.exceptions.ConnectionError: http://ip.jsontest.com
{'ip': '8.8.8.8'}
>>> obj = Class()
>>> obj.stat_meth()
WARNING: Function threw exception below on try 1, retrying in 0.404934 seconds
Traceback (most recent call last):
  ...
requests.exceptions.ConnectionError: http://ip.jsontest.com
{'ip': '8.8.8.8'}
>>> obj.prop
WARNING: Function threw exception below on try 1, retrying in 0.303313 seconds
Traceback (most recent call last):
  ...
requests.exceptions.ConnectionError: http://ip.jsontest.com
{'ip': '8.8.8.8'}
```
