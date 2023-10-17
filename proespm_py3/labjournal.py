from __future__ import annotations
from dateutil.parser import parse
from datetime import datetime
import pandas as pd


NUM_HEADER_ROWS = 5


class LabJournal:
    """Class handeling a excel spreadsheet as a labjournal"""

    def __init__(self, xls_file: str) -> None:
        self.excel = pd.ExcelFile(xls_file)
        self.sheet_names = self.excel.sheet_names

    def read_header(self, sheet_name: str) -> LabJournalHeader:
        return LabJournalHeader(self.excel, sheet_name)

    def read_entries(self, sheet_name: str):
        self.excel.parse(skriprows=5, sheet_name=sheet_name)


class LabJournalHeader:
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
                if type(df.loc["day"] != pd.Series)
                else df.loc["day"][1]
            )
            title = (
                df.loc["title"]
                if type(df.loc["title"] != pd.Series)
                else df.loc["title"][1]
            )
            experimenters = (
                df.loc["experimenters"]
                if type(df.loc["experimenters"] != pd.Series)
                else df.loc["experimenters"][1]
            )
            comment = (
                df.loc["comment"]
                if type(df.loc["comment"] != pd.Series)
                else df.loc["comment"][1]
            )
            identifier = (
                df.loc["identifier"]
                if type(df.loc["identifier"] != pd.Series)
                else df.loc["identifier"][1]
            )
            self.day = parse(day_str)
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
