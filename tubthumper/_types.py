"""Module of types used in tubthumper"""

import sys
from typing import (
    Any,
    Awaitable,
    Callable,
    Iterable,
    Mapping,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
)

if sys.version_info >= (3, 8):
    from typing import Protocol
else:
    from typing_extensions import Protocol


Exceptions = Union[Type[Exception], Tuple[Type[Exception]]]
Args = Optional[Iterable[Any]]
Kwargs = Optional[Mapping[str, Any]]
RetryLimit = float
TimeLimit = float
InitBackoff = float
Exponential = float
Jitter = bool
Reraise = bool
LogLevel = int

T = TypeVar("T")
RetryCallable = Callable[..., T]
AwaitableCallable = Callable[..., Awaitable[T]]
Decorator = Callable[[RetryCallable[T]], RetryCallable[T]]


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
