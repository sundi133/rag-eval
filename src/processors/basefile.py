import pandas as pd
import os
import json
from typing import List
from abc import ABC, abstractmethod

# TODO - Implement proper abstractions and oo design with logging
# TODO - Implement proper error handling

class FileProcessor:
    def __init__(self, data_path: str) -> None:
        self.data_path = data_path
        self.file_extension = os.path.splitext(data_path)[-1].lower()

    @abstractmethod
    def parse(self):
        pass

    @abstractmethod
    def get_randomized_samples(self,
        data: pd.DataFrame,
        sample_size: int,
        products_group_size: int,
        group_columns: List[str],):
        pass

    @abstractmethod
    def write(self, file_path: str, data: json) -> None:
        pass
