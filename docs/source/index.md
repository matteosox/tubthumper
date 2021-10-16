```{testsetup}
import logging

import requests
from requests import ConnectionError

from docs.test import setup

setup()


class Response:
    """Mock a response to requests.get that succeeds every 3rd time"""

    def __init__(self):
        self.counter = 0

    def __call__(self, url):
        self.counter += 1
        if self.counter % 3:
            raise ConnectionError(url)
        return self

    @staticmethod
    def json():
        """Spoofed json method of response"""
        return {"ip": "8.8.8.8"}

requests.get = Response()

def get_ip(*_args, **_kwargs):
    """Example function that needs retrying"""
    return requests.get("http://ip.jsontest.com").json()

# Spoof main script
__name__ = "__main__"

```

```{include} ../build/README.md
```

```{toctree}
:hidden:

Overview <self>
recipes.md
api.rst
credits.md
changelog.md
contributor_guide.md
Report an Issue <https://github.com/matteosox/tubthumper/issues>
GitHub <https://github.com/matteosox/tubthumper>
PyPI <https://pypi.org/project/tubthumper>
```
