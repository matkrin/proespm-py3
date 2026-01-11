import datetime
from abc import ABC, abstractmethod
from typing import Self

from proespm.config import Config


class Measurement(ABC):
    """Interface for a scientific measurement file."""

    @abstractmethod
    def __init__(self, filepath: str) -> None: ...

    @abstractmethod
    def m_id(self) -> str:
        """Unique measurement identifier."""
        ...

    @abstractmethod
    def datetime(self) -> datetime.datetime:
        """Date and time of the measurement."""
        ...

    @abstractmethod
    def process(self, config: Config) -> Self:
        """Processing of the measurement."""
        ...

    @abstractmethod
    def template_name(self) -> str | None:
        """Name of the Jinja2 template used for HTML rendering."""
        ...
