"""Module of types used in tubthumper"""

import sys
from typing import Any, Iterable, Mapping, Optional, Tuple, Type, TypeVar, Union

if sys.version_info < (3, 10):
    from typing_extensions import ParamSpec, Protocol, TypeAlias
else:
    from typing import ParamSpec, Protocol, TypeAlias


Exceptions: TypeAlias = Union[Type[Exception], Tuple[Type[Exception], ...]]
Args: TypeAlias = Optional[Iterable[Any]]
Kwargs: TypeAlias = Optional[Mapping[str, Any]]
RetryLimit: TypeAlias = float
Exponential: TypeAlias = float
Jitter: TypeAlias = bool
Reraise: TypeAlias = bool
LogLevel: TypeAlias = int
Duration: TypeAlias = float

T = TypeVar("T")
P = ParamSpec("P")


class Logger(Protocol):
    """
    Generally a `logging.Logger`, but since we want to support
    `duck-typing <https://docs.python.org/3/glossary.html#term-duck-typing>`_,
    this is a `typing.Protocol` to enable
    `structural subtyping <https://www.python.org/dev/peps/pep-0544/>`_.
    """

    def log(self, level: int, msg: str, *args: object, exc_info: bool) -> None:
        r"""We call this method to log at the configured level with ``exc_info=True``

        Args:
            level:
                the level of the message to be logged
            msg:
                the message to be logged
            exc_info:
                causes exception information to be added to the logging message
        """
