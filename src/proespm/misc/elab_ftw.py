from __future__ import annotations
from typing import Any, Hashable, Self, final, override
from proespm.config import Config
from proespm.measurement import Measurement
import json
from datetime import datetime

import html
from bs4 import BeautifulSoup


def extract_elabftw(filepath: str) -> list[ElabFtw]:
    with open(filepath, "r") as f:
        json_content = json.load(f)  # pyright: ignore[reportAny]

    entries = _parse_html_body(json_content["body_html"])  # pyright: ignore[reportAny]
    return [
        ElabFtw(
            timestamp=k,
            text=v,
            number=i + 1,
            json_content=json_content,  # pyright: ignore[reportAny]
        )
        for i, (k, v) in enumerate(entries.items())
    ]


@final
class ElabFtw(Measurement):
    def __init__(
        self,
        timestamp: datetime,
        text: str,
        number: int,
        json_content: dict[Hashable, Any],  # pyright: ignore[reportExplicitAny]
    ) -> None:
        self._datetime = timestamp
        self.text = text
        self._number = number

        self.title: str = json_content["title"]
        self.type_: str = json_content["type"]
        self.operator: str = json_content["fullname"]
        self.team: str = json_content["team_name"]
        self.tags: str = json_content["tags"]

    @override
    def m_id(self) -> str:
        return f"{self.title} - {self._number}"

    @override
    def datetime(self) -> datetime:
        return self._datetime

    @override
    def process(self, config: Config) -> Self:
        return self

    @override
    def template_name(self) -> str | None:
        return "elab_ftw.j2"


def _parse_html_body(raw_string: str) -> dict[datetime, str]:
    """Parsing of timestamps and corresponding text from escaped HTML tables.

    Returns
    A ist of dicts: {timestamp: datetime | str, text: str}
    """

    # 1. Unescape \u003C etc. into real HTML
    html_string = html.unescape(raw_string)

    # 2. Parse HTML
    soup = BeautifulSoup(html_string, "html.parser")

    entries: dict[datetime, str] = dict()

    # 3. Iterate over table rows
    for tr_tag in soup.find_all("tr"):
        td_tag = tr_tag.find_all("td")
        if len(td_tag) != 2:
            continue

        time_cell, text_cell = td_tag

        timestamps = [
            t.strip() for t in time_cell.stripped_strings if t.strip()
        ]

        texts = [t.strip() for t in text_cell.stripped_strings if t.strip()]

        if len(timestamps) == len(texts):
            for ts, txt in zip(timestamps, texts):
                entries.update({datetime.fromisoformat(ts): txt})
        else:
            combined_text = " ".join(texts)
            for ts in timestamps:
                entries.update({datetime.fromisoformat(ts): combined_text})

    return entries
