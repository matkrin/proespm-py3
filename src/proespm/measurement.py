from abc import ABC, abstractmethod
from typing import Self

from proespm.config import Config


class Measurement(ABC):
    @abstractmethod
    def process(self, config: Config) -> Self: ...

    @abstractmethod
    def template_name(self) -> str | None: ...
