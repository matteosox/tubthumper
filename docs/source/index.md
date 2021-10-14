```{testsetup}
import logging
import random
import time

import requests
from requests import ConnectionError

# Make backoff periods consistent
random.seed(0)
# Don't actually sleep
time.sleep = lambda arg: None
# Spoof main script
__name__ = "__main__"
# Set logger's handler to print to get doctest to work
logger = logging.getLogger("tubthumper")


class PrintHandler(logging.Handler):
    def emit(self, record):
        msg = self.format(record)
        print(msg)


print_handler = PrintHandler()
formatter = logging.Formatter('%(levelname)s: %(message)s')
print_handler.setFormatter(formatter)
logger.addHandler(print_handler)


# Mock a response to requests.get that fails every other time
class Response:
    def __call__(self, url):
        self.fail = not getattr(self, "fail", False)
        if self.fail:
            raise ConnectionError(url)
        return self

    def json(self):
        return {"ip": "8.8.8.8"}


requests.get = Response()


def get_ip(*args, **kwargs):
    return requests.get("http://ip.jsontest.com").json()


def fails_often(arg=[0]):
    arg[0] += 1
    if arg[0] % 3:
        raise Exception

```

```{include} ../../README.md
```

```{toctree}
:hidden:

Overview <self>
api.rst
credits.md
changelog.md
contributor_guide.md
Report an Issue <https://github.com/matteosox/tubthumper/issues>
GitHub <https://github.com/matteosox/tubthumper>
PyPI <https://pypi.org/project/tubthumper>
```
