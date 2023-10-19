from __future__ import annotations
from typing import TYPE_CHECKING
from dateutil.parser import ParserError, parse
from datetime import datetime
import numpy as np
import pandas as pd

from proespm_py3.ec.ec4 import Ec4


if TYPE_CHECKING:
    from .proespm_py3 import DataObject


NUM_HEADER_ROWS = 5


class LabJournal:
    """Class handeling a excel spreadsheet as a labjournal"""

    def __init__(self, xls_file: str) -> None:
        self.excel = pd.ExcelFile(xls_file)
        self.sheet_names = self.excel.sheet_names
        self.used_sheets: list[str] = []
        self.read_entries()

    def read_header(self) -> list[LabJournalHeader]:
        """Return the labjournal headers that were in use in extraction"""
        return [
            LabJournalHeader(self.excel, used_sheet)
            for used_sheet in set(self.used_sheets)
        ]

    def read_entries(self):
        entries = self.excel.parse(
            skiprows=NUM_HEADER_ROWS, sheet_name=None, dtype=str
        )
        assert type(entries) == dict
        self.entries = {
            key: self.expand_entries(value) for (key, value) in entries.items()
        }  # type: ignore

    @staticmethod
    def expand_entries(entries: pd.DataFrame) -> pd.DataFrame:
        """Expand the labjournal entries to cover all files that were just
        mentioned via last_ID
        """
        new_entries = []
        for first_id, last_id in zip(entries["first_ID"], entries["last_ID"]):
            if not pd.isna(last_id) and not pd.isna(first_id):
                last_id_int = int(last_id)
                num_digits = len(str(last_id_int))
                id_base, last_num = first_id[:-num_digits], int(
                    first_id[-num_digits:]
                )
                for i in range(last_num + 1, last_id_int + 1):
                    new_id = f"{id_base}{i}"
                    entry = entries[
                        entries["first_ID"].str.match(first_id, na=False)
                    ].copy()
                    entry["first_ID"] = new_id
                    entry["last_ID"] = np.nan
                    new_entries.append(entry)
        return pd.concat([entries, *new_entries])

    def extract_entry(self, data_obj: DataObject) -> None:
        """Extract labjournal entries for data_obj

        Args:
            data_obj: The DataObject for which is extracted
        """
        m_id = data_obj.m_id
        if type(data_obj) == Ec4:
            m_id = m_id.rsplit("_", 1)[0]

        for sheet in self.sheet_names:
            df = self.entries[sheet]
            matched_row = df[df["first_ID"].str.match(m_id, na=False)]
            if len(matched_row.index) == 0:
                continue
            if type(matched_row) == pd.DataFrame:
                row_dict = matched_row.to_dict(orient="list")
                self.used_sheets.append(str(sheet))
                for key, value in row_dict.items():
                    setattr(data_obj, key, value[0])

    def close(self):
        """Close the excel file"""
        self.excel.close()


class LabJournalHeader:
    """Class for the labjournal header (first lines of a spreadsheet)"""

    def __init__(self, excel: pd.ExcelFile, sheet_name: str) -> None:
        df = excel.parse(
            nrows=NUM_HEADER_ROWS,
            index_col=0,
            header=None,
            sheet_name=sheet_name,
        )
        if type(df) == pd.DataFrame:
            day_str = (
                df.loc["day"]
                if type(df.loc["day"]) != pd.Series
                else df.loc["day"][1]
            )
            title = (
                df.loc["title"]
                if type(df.loc["title"]) != pd.Series
                else df.loc["title"][1]
            )
            experimenters = (
                df.loc["experimenters"]
                if type(df.loc["experimenters"]) != pd.Series
                else df.loc["experimenters"][1]
            )
            comment = (
                df.loc["comment"]
                if type(df.loc["comment"]) != pd.Series
                else df.loc["comment"][1]
            )
            identifier = (
                df.loc["identifier"]
                if type(df.loc["identifier"]) != pd.Series
                else df.loc["identifier"][1]
            )
            try:
                assert type(day_str) == str  # for typing
                self.day = parse(day_str)
            except ParserError:
                self.day = datetime(1970, 1, 1)
            self.title = title
            self.experimenters = experimenters
            self.comment = comment
            self.identifier = identifier
        else:
            self.day = datetime(1970, 1, 1)
            self.title = "No title found"
            self.experimenters = "No experimenters found"
            self.comment = "No comment found"
            self.identifier = "No identifier found"
