import os
import pandas as pd
import json
import io
import logging
import random
import time

from langchain.chains import LLMChain
from langchain.callbacks import get_openai_callback  # For OpenAI models

from typing import List
from .basefile import DataProcessor
from ..models import QAData
from sqlalchemy.orm import Session
from datetime import datetime
from fastapi_sqlalchemy import DBSessionMiddleware, db

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
ch = logging.StreamHandler()
ch.setFormatter(formatter)
logger.addHandler(ch)


class TXTProcessor(DataProcessor):
    def __init__(self, data_path: List[str], dataset_id: str) -> None:
        super().__init__(data_path, dataset_id)
        self.qa_dict = {}
        self.qa_array = []
        self.batch_size = 25
        self.chunk_size = 2000

    def setTenant(self, tenant: str) -> None:
        super().setTenant(tenant)

    def setUser(self, user: str) -> None:
        super().setUser(user)

    def setSimProfile(self, profile: dict) -> None:
        super().setSimProfile(profile)

    def parse(self) -> pd.DataFrame:
        combined_content = ""
        for data in self.data_path:
            with open(data, "r") as f:
                file_content = f.read()
                combined_content += file_content

        # Clean the combined text
        data = self.recursive_chunk_split(combined_content)
        df = pd.DataFrame({"chunk": data})
        df["chunk"] = df["chunk"].apply(lambda x: x.strip())
        df = df[df["chunk"].notna() & (df["chunk"] != "")].reset_index(drop=True)

        return df

    def randomize_samples(
        self,
        data: pd.DataFrame,
        sample_size: int,
        products_group_size: int,
        group_columns: List[str],
    ) -> pd.DataFrame:
        sample = data.shape[0] * (int(sample_size / 100) + 1)
        if sample > data.shape[0]:
            sample = data.shape[0]

        return data.sample(n=sample, random_state=42)

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
        for _index, group_row in randomized_samples.iterrows():
            try:
                records = group_row["chunk"]

                if len(records) < 100:
                    continue

                if (
                    number_of_questions > self.batch_size
                ):  # too many questions might cause token limit error
                    number_of_questions = self.batch_size

                logger.info(
                    {
                        "message": "check qa_generator",
                        "qa_generator": qa_generator.prompt.input_variables,
                    }
                )
                if (
                    "chunk_reference_first" in qa_generator.prompt.input_variables
                    and "chunk_reference_second" in qa_generator.prompt.input_variables
                ):
                    # Define window boundaries based on current index
                    window_indices = [
                        _index + i
                        for i in range(
                            -self.chunk_reference_max_distance,
                            self.chunk_reference_max_distance,
                        )
                        if 0 <= _index + i < randomized_samples.shape[0] and i != 0
                    ]
                    desired_index = window_indices[-1]
                    row_content = randomized_samples.iloc[desired_index]

                    # Check if "chunk" column exists, otherwise access the entire row
                    chunk_reference_second = row_content["chunk"]

                    with get_openai_callback() as cb:
                        qa_pair = qa_generator.run(
                            chunk_reference_first=records,
                            chunk_reference_second=chunk_reference_second,
                            number_of_questions=number_of_questions,
                            persona=self.sim_profile["persona"],
                        )
                        records = (
                            records
                            + "\n\n"
                            + "Distant reference chunk: "
                            + chunk_reference_second
                        )
                        logger.info(
                            {
                                "total_tokens": cb.total_tokens,
                                "total_cost": cb.total_cost,
                            }
                        )
                else:
                    with get_openai_callback() as cb:
                        qa_pair = qa_generator.run(
                            products=records,
                            number_of_questions=number_of_questions,
                            persona=self.sim_profile["persona"],
                        )
                        logger.info(
                            {
                                "total_tokens": cb.total_tokens,
                                "total_cost": cb.total_cost,
                            }
                        )

                question_array = json.loads(qa_pair)

                qadata = []
                for record in question_array:
                    qadata.append(record)

                self.add_output_sample(qadata, chunk=records)

            except Exception as e:
                logger.error(
                    {
                        "message": "Error generating question",
                        "error": str(e),
                    }
                )
                continue
        return self.qa_dict

    def add_output_sample(self, records: List[dict], chunk: str) -> None:
        super().add_output_sample(records, chunk=chunk)

    def write(self, file_path: str) -> None:
        pass

    def write_to_db(self, dataset_id: str, status: str, message: str) -> None:
        super().write_to_db(dataset_id, status, message)
