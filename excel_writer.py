import pandas as pd
from pathlib import Path
from typing import Dict, List, Any


class ExcelOutputWriter:
    def __init__(self, file_path: str):
        self._file_path = Path(file_path)

    def write(self, sheets: Dict[str, List[Dict[str, Any]]]):

        with pd.ExcelWriter(self._file_path, engine="openpyxl") as writer:
            for sheet_name, data in sheets.items():
                df = pd.DataFrame(data)
                df.to_excel(writer, sheet_name=sheet_name, index=False)