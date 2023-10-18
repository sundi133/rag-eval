import pandas as pd
import os
import json
from typing import List
from abc import ABC, abstractmethod
from langchain.chains import LLMChain

# TODO - Implement proper abstractions and oo design with logging
# TODO - Implement proper error handling


class DataProcessor:
    def __init__(self, data_path: str) -> None:
        self.data_path = data_path
        self.file_extension = os.path.splitext(data_path)[-1].lower()
        self.qa_dict = {}

    @abstractmethod
    def parse(self):
        pass

    @abstractmethod
    def get_randomized_samples(
        self,
        data: pd.DataFrame,
        sample_size: int,
        products_group_size: int,
        group_columns: List[str],
    ):
        pass

    @abstractmethod
    def generate_qa_pairs(
        self,
        randomized_samples: pd.DataFrame,
        df: pd.DataFrame,
        sample_size: int,
        products_group_size: int,
        group_columns: List[str],
        number_of_questions: int,
        qa_generator: LLMChain,
    ) -> None:
        pass

    @abstractmethod
    def add_output_sample(self):
        pass

    @abstractmethod
    def write(self, file_path: str) -> None:
        pass
