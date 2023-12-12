import pandas as pd
import os
from typing import List
from abc import ABC, abstractmethod
from langchain.chains import LLMChain
import random
import time
import json

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

    @staticmethod
    def retry_with_exponential_backoff(
        func,
        initial_delay: float = 1,
        exponential_base: float = 2,
        jitter: bool = True,
        max_retries: int = 10,
    ):
        """Retry a function with exponential backoff."""

        def wrapper(*args, **kwargs):
            # Initialize variables
            num_retries = 0
            delay = initial_delay

            # Loop until a successful response or max_retries is hit or an exception is raised
            while True:
                try:
                    return func(*args, **kwargs)

                # Retry on specific errors
                except (
                    TimeoutError,
                    ConnectionError,
                    ConnectionAbortedError,
                    ConnectionRefusedError,
                    ConnectionResetError,
                    json.decoder.JSONDecodeError,
                ) as e:
                    # Increment retries
                    num_retries += 1

                    # Check if max retries has been reached
                    if num_retries > max_retries:
                        raise Exception(
                            f"Maximum number of retries ({max_retries}) exceeded."
                        )

                    # Increment the delay
                    delay *= exponential_base * (1 + jitter * random.random())

                    # Sleep for the delay
                    time.sleep(delay)

                # Raise exceptions for any errors not specified
                except Exception as e:
                    raise e

        return wrapper
