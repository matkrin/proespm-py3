import datetime
from abc import ABC, abstractmethod
from typing import Self

from proespm.config import Config


class Measurement(ABC):
    @abstractmethod
    def m_id(self) -> str:...

    @abstractmethod
    def datetime(self) -> datetime.datetime: ...

    @abstractmethod
    def process(self, config: Config) -> Self: ...

    @abstractmethod
    def template_name(self) -> str | None: ...
