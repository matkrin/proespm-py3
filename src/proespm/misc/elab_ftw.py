from typing import Self, final, override
from proespm.config import Config
from proespm.measurement import Measurement
import json
from datetime import datetime


@final
class ElabFtw(Measurement):
    def __init__(self, filepath: str) -> None:
        with open(filepath, "r") as f:
            json_content = json.load(f)  # pyright: ignore[reportAny]

        self._datetime = datetime.fromisoformat(json_content["created_at"])  # pyright: ignore[reportAny]
        self.title: str = json_content["title"]
        self.type_: str = json_content["type"]
        self.body_html: str = json_content["body_html"]
        self.operator: str = json_content["fullname"]
        self.team: str = json_content["team_name"]
        self.tags: str = json_content["tags"]

    @override
    def m_id(self) -> str:
        return self.title

    @override
    def datetime(self) -> datetime:
        return self._datetime

    @override
    def process(self, config: Config) -> Self:
        return self

    @override
    def template_name(self) -> str | None:
        return "elab_ftw.j2"
