import os
import pandas as pd
from typing import List
from .basefile import DataProcessor


class PDFProcessor(DataProcessor):
    def __init__(self, data_path: str) -> None:
        super().__init__(data_path)
        self.file_extension = os.path.splitext(data_path)[-1].lower()
        self.data = self.parse()

    def parse(self) -> pd.DataFrame:
        pass

    def randomize_samples(
        self,
        data: pd.DataFrame,
        sample_size: int,
        products_group_size: int,
        group_columns: List[str],
    ) -> pd.DataFrame:
        pass

    def write(self, file_path: str) -> None:
        pass
