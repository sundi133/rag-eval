from processors.basefile import FileProcessor
import os
import pandas as pd
import os
import json
from typing import List
from abc import ABC, abstractmethod


class PGSQLProcessor(FileProcessor):
    def __init__(self, data_path: str) -> None:
        super().__init__(data_path)
        self.file_extension = os.path.splitext(data_path)[-1].lower()
        self.data = self.parse()

    def parse(self) -> pd.DataFrame:
        pass

    def get_randomized_samples(
        self,
        data: pd.DataFrame,
        sample_size: int,
        products_group_size: int,
        group_columns: List[str],
    ) -> pd.DataFrame:
        pass

    def write(self, file_path: str, data: json) -> None:
        pass
