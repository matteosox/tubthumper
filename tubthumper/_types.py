"""Module of types used in tubthumper"""

import sys
from typing import Any, Iterable, Mapping, Optional, Tuple, Type, TypeVar, Union

if sys.version_info >= (3, 8):
    from typing import Protocol
else:
    from typing_extensions import Protocol


__all__ = ["LoggerType"]

ExceptionsType = Union[Type[Exception], Tuple[Type[Exception]]]
ArgsType = Optional[Iterable]
KwargsType = Optional[Mapping[str, Any]]
RetryLimitType = Union[int, float]
TimeLimitType = Union[int, float]
InitBackoffType = Union[int, float]
ExponentialType = Union[int, float]
JitterType = bool
ReraiseType = bool
LogLevelType = int
ReturnType = TypeVar("ReturnType")


class LoggerType(Protocol):
    """
    Generally a `logging.Logger`, but since we want to support
    `duck typing <https://docs.python.org/3/glossary.html#term-duck-typing>`_,
    this is a `typing.Protocol` to enable
    `structural subbtyping <https://www.python.org/dev/peps/pep-0544/>`_.
    """

    def log(self, level: int, msg: str, exc_info: bool, **kwargs: Any) -> Any:
        r"""
        We call this method to log at the configured level with ``exc_info=True``

        :param level:
            the level of the message to be logged
        :param msg:
            the message to be logged
        :param exc_info:
            causes exception information to be added to the logging message
        """
