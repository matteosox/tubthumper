```{testsetup}
import requests
from requests import ConnectionError

# Spoof main script
__name__ = "__main__"

URL = "http://ip.jsontest.com"
JSON = {"ip": "8.8.8.8"}

# Mock a response to requests.get
class Response:
    def __init__(self):
        self.counter = 0

    def __call__(self, url):
        self.counter += 1
        if self.counter % 3:
            raise ConnectionError(URL)
        return self

    def json(self):
        return JSON


requests.get = Response()


def get_ip(*args, **kwargs):
    return requests.get(URL).json()

```

```{include} ../build/readme.md
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
