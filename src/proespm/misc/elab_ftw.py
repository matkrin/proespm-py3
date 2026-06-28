from __future__ import annotations

import html
import json
import re
import warnings
from datetime import datetime
from pathlib import Path
from typing import Any, Self, final, override

from bs4 import BeautifulSoup

from proespm.config import Config
from proespm.measurement import Measurement

_COLOR_PALETTE = [
    "#5B8DB8", "#E8A838", "#7CBB7A", "#C47AC0", "#6BBFBE",
    "#E07B5A", "#9B8DC8", "#B5C45A", "#D4857A", "#5AA0A0",
]


def extract_elabftw(filepath: Path) -> list[ElabFtw]:
    with open(filepath) as f:
        json_content = json.load(f)

    entries = _parse_html_body(
        json_content.get("body") or json_content.get("body_html", "")
    )
    return [
        ElabFtw(row=entry, number=i + 1, json_content=json_content)
        for i, entry in enumerate(entries)
    ]


@final
class ElabFtw(Measurement):
    measurement_family = "ElabFTW"

    def __init__(
        self,
        row: dict[str, Any],
        number: int,
        json_content: dict[str, Any],
    ) -> None:
        self._datetime: datetime = row["timestamp"]
        self.text: str = row["content_html"]
        self._number = number
        self.initials: str = row["initials"]
        self.app_version: str = row["app_version"]

        self.elab_id: int = json_content["id"]
        is_experiment = json_content.get("type") == "experiments"
        self.is_experiment: bool = is_experiment

        self.title: str = json_content.get("title", "")
        self.type_: str = "experiment" if is_experiment else "resource"
        self.operator: str = json_content.get("fullname") or ""
        self.team: str = json_content.get("team_name") or ""
        self.tags: str = json_content.get("tags") or ""

        self.border_color: str = _COLOR_PALETTE[self.elab_id % len(_COLOR_PALETTE)]
        self.border_style: str = "solid" if is_experiment else "dashed"

    @override
    def m_id(self) -> str:
        return f"{self.title} (#{self.elab_id}) - {self._number}"

    @override
    def get_datetime(self) -> datetime:
        return self._datetime

    @override
    def process(self, config: Config) -> Self:
        return self

    @override
    def template_name(self) -> str | None:
        return "elab_ftw.j2"


def _parse_html_body(raw_string: str) -> list[dict[str, Any]]:
    html_string = html.unescape(raw_string)
    soup = BeautifulSoup(html_string, "html.parser")

    entries: list[dict[str, Any]] = []

    for table in soup.find_all("table"):
        # Identify elab-app log tables by their signature identifier row
        rows = table.find_all("tr")
        is_elab_table = any(
            (cells := tr.find_all("td"))
            and cells[0].get_text(strip=True) == "elab_app"
            for tr in rows
        )
        if not is_elab_table:
            continue

        for tr in rows:
            # Skip header rows
            if tr.find("th"):
                continue

            cells = tr.find_all("td")
            if not cells:
                continue

            # Skip identifier row
            if cells[0].get_text(strip=True) == "elab_app":
                continue

            # Skip system back-reference rows
            if len(cells) >= 3 and cells[2].get_text(strip=True) == "#":
                continue

            app_version = cells[3].get_text(strip=True) if len(cells) >= 4 else "2.x"

            entries.append({
                "timestamp": datetime.fromisoformat(cells[0].get_text(strip=True)),
                "content_html": cells[1].decode_contents().strip(),
                "initials": cells[2].get_text(strip=True),
                "app_version": app_version,
            })

    # Warn for unexpected future versions (not v2.x legacy sentinel, not v2.* or v3.*)
    for entry in entries:
        ver = entry["app_version"]
        if ver != "2.x" and not re.match(r"^v[23]\.", ver):
            warnings.warn(
                f"elab-app row version '{ver}' is not understood by this parser; "
                "row may not display correctly"
            )

    return entries
