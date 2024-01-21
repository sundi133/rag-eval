import os
import pandas as pd

from typing import List
from .basefile import DataProcessor


class PGSQLProcessor(DataProcessor):
    def __init__(self, data_path: str, dataset_id: str) -> None:
        super().__init__(data_path, dataset_id)
        self.file_extension = os.path.splitext(data_path)[-1].lower()
        self.data = self.parse()

    def parse(self) -> pd.DataFrame:
        pass

    def setTenant(self, tenant: str) -> None:
        super().setTenant(tenant)

    def setUser(self, user: str) -> None:
        super().setUser(user)

    def setSimProfile(self, profile: dict) -> None:
        super().setSimProfile(profile)

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

    def write_to_db(self, dataset_id: str, status: str, message: str) -> None:
        super().write_to_db(dataset_id, status, message)
