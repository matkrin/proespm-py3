from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Hashable, override

import numpy as np
import pandas as pd
from dateutil.parser import ParserError, parse


NUM_HEADER_ROWS = 5


class Labjournal(ABC):
    """The interface for a Labjournal"""

    @abstractmethod
    def extract_metadata_for_m_id(
        self, m_id: str
    ) -> dict[Hashable, Any] | None: ...


def parse_labjournal(xls_file: str) -> Labjournal:
    """Parses a Labjournal Excel file.

    Args:
        xls_file: Path to the Excel file.

    Returns:
        Depending on the content of the file, a `LabjournalSimple` or a
        `LabjournalStructured`.
    """
    df = pd.read_excel(xls_file, dtype=str)
    if df["day"].iloc[1] == "experimenters":
        return LabjournalStructured(xls_file)

    return LabjournalSimple(xls_file)


class LabjournalSimple(Labjournal):
    """Class for handling a simple labjournal Excel file. The file only
    contains a one line of header, followed by rows of entries.

    Args:
        xls_file: Path to the Excel file.
    """

    def __init__(self, xls_file: str) -> None:
        self._excel: pd.DataFrame = pd.read_excel(xls_file, dtype=str)

    @override
    def extract_metadata_for_m_id(
        self, m_id: str
    ) -> dict[Hashable, Any] | None:
        matched_row = self._excel[self._excel["ID"].str.match(m_id)]
        row_dict = matched_row.to_dict(orient="list")
        if len(matched_row.index) == 0:
            return None

        return row_dict


class LabjournalStructured(Labjournal):
    """Class for handling a more structured labjournal Excel file.
    The file contains a header giving detailed information about
    measurement context and metadata.

    Args:
        xls_file: Path to the Excel file.
    """

    def __init__(self, xls_file: str) -> None:
        self._excel_file = pd.ExcelFile(xls_file)
        self._sheet_names = self._excel_file.sheet_names
        self._used_sheets: list[str] = []
        self._entries: dict[str, pd.DataFrame] = self._read_entries()

    def _read_header(self) -> list[LabJournalHeader]:
        """Read the labjournal headers that were in use in extraction"""
        return [
            LabJournalHeader(self._excel_file, used_sheet)
            for used_sheet in set(self._used_sheets)
        ]

    def _read_entries(self) -> dict[str, pd.DataFrame]:
        """Read the labjournal entries and expand with additional entries, if
        a range of IDs is given in the entry."""
        entries = self._excel_file.parse(
            skiprows=NUM_HEADER_ROWS, sheet_name=None, dtype=str
        )
        assert isinstance(entries, dict)
        return {
            str(key): expand_labjournal_entries(value)
            for (key, value) in entries.items()
        }

    @override
    def extract_metadata_for_m_id(
        self, m_id: str
    ) -> dict[Hashable, Any] | None:
        """Extract labjournal entries for measurement IDs (m_id)

        Args:
            m_id: The measurement ID of a `ProcessObject`.

        Returns:
            The metadata in the Excel file for the given `m_id`.
        """
        for sheet in self._sheet_names:
            df = self._entries[sheet]
            matched_row = df[df["first_ID"].str.match(m_id, na=False)]

            if len(matched_row.index) == 0:
                continue

            row_dict = matched_row.to_dict(orient="list")
            self._used_sheets.append(str(sheet))
            return row_dict

        return None

    def close(self):
        """Close the excel file"""
        self._excel_file.close()

    # def detect_missing_files(self, data_objs: list[DataObject]) -> list[str]:
    #     """Detects files for which entries exist but that are missing"""
    #     missing_files: list[str] = []
    #     for sheet in set(self.used_sheets):
    #         for entry_id in self.entries[sheet]["first_ID"]:
    #             if (
    #                 entry_id not in [obj.m_id for obj in data_objs]
    #                 and entry_id is not np.nan
    #             ):
    #                 missing_files.append(entry_id)
    #
    #     return missing_files

    @override
    def __repr__(self) -> str:
        fields_repr = ",\n\t".join(
            f"{key}={repr(value)}"
            for key, value in self.__dict__.items()  # pyright: ignore[reportAny]
        )
        return f"{self.__class__.__name__}(\n{fields_repr}\n)"


class LabJournalHeader:
    """Class for the labjournal header (first lines of a spreadsheet) of a
    `LabjournalStructured`.

    Args:
        excel: The Excel file as a `pd.ExcelFile`.
        sheet_name: Name of the sheet in the Excel file, for which the
            header is constructed.
    """

    def __init__(self, excel: pd.ExcelFile, sheet_name: str) -> None:
        self.sheet_id = str(sheet_name)
        df = excel.parse(
            nrows=NUM_HEADER_ROWS,
            index_col=0,
            header=None,
            sheet_name=sheet_name,
        )
        day_str = str(df.loc["day"][1])
        try:
            self.day = parse(day_str)
        except ParserError:
            self.day = datetime(1970, 1, 1)
        self.title = df.loc["title"][1]
        self.experimenters = df.loc["experimenters"][1]
        self.comment = df.loc["comment"][1]
        self.identifier = df.loc["identifier"][1]

    @override
    def __repr__(self) -> str:
        fields_repr = ",\n\t".join(
            f"{key}={repr(value)}"
            for key, value in self.__dict__.items()  # pyright: ignore[reportAny]
        )
        return f"{self.__class__.__name__}(\n{fields_repr}\n)"


def expand_labjournal_entries(df: pd.DataFrame) -> pd.DataFrame:
    """Expand the labjournal entries to cover all files that were just
    mentioned via last_ID."""
    new_entries = []
    for first_id, last_id in zip(df["first_ID"], df["last_ID"]):
        if not pd.isna(last_id) and not pd.isna(first_id):
            entry = df[df["first_ID"].str.match(first_id, na=False)]

            if entry["type"].iloc[0].endswith("ps"):
                id_base, first_id_int, last_id_int = parse_palm_sense(
                    first_id, last_id
                )
                separator = "-"

            else:
                last_id_int = int(last_id)
                num_digits = len(str(last_id_int))
                id_base, first_id_int = (
                    first_id[:-num_digits],
                    int(first_id[-num_digits:]),
                )
                separator = ""

            # Entry with `first_id_int` is already in entries
            for i in range(first_id_int + 1, last_id_int + 1):
                new_m_id = f"{id_base}{separator}{i}"
                entry = df[df["first_ID"].str.match(first_id, na=False)].copy()
                entry["first_ID"] = new_m_id
                entry["last_ID"] = np.nan
                new_entries.append(entry)

    return pd.concat([df, *new_entries])


def parse_palm_sense(first_id: str, last_id: str) -> tuple[str, int, int]:
    """Parses the name of file measured via PalmSense potentiostat."""
    id_base, first_id_str = first_id.rsplit("-", maxsplit=1)
    first_id_int = int(first_id_str)
    last_id_int = int(last_id)
    return id_base, first_id_int, last_id_int
