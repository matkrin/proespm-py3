import pandas as pd


class Labjournal:
    def __init__(self, excel_file: str) -> None:
        self.excel: pd.DataFrame = pd.read_excel(excel_file, dtype=str)

    def extract_metadata_for_m_id(self, m_id: str) -> dict[str, list[str]]:
        matched_row = self.excel[self.excel["ID"].str.match(m_id)]
        row_dict = matched_row.to_dict(orient="list")
        # _ = row_dict.pop("ID")
        return row_dict

