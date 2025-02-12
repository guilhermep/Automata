import abc
from typing import Any


class Singleton(abc.ABCMeta, type):
    """An abstract metaclass for ensuring only one instance of a class."""

    _instance: Any = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Singleton, cls).__new__(cls, *args, **kwargs)
        return cls._instance
