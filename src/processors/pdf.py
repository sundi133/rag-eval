import os
import pandas as pd
import json
import io
import logging
import random
import time
import fitz

from langchain.chains import LLMChain
from typing import List
from .basefile import DataProcessor
from .txt import TXTProcessor
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


class PDFProcessor(TXTProcessor):
    def __init__(self, data_path: str, dataset_id: str) -> None:
        super().__init__(data_path, dataset_id)

    def parse(self) -> pd.DataFrame:
        combined_content = ""
        for data in self.data_path:
            with open(data, "rb") as file:
                pdf_document = fitz.open(data)

                text = ""
                for page_num in range(pdf_document.page_count):
                    page = pdf_document[page_num]
                    text += page.get_text()

                combined_content += text
                pdf_document.close()
        combined_content = self.clean_text_to_ascii(combined_content)

        data = self.recursive_chunk_split(combined_content)

        df = pd.DataFrame({"chunk": data})
        df["chunk"] = df["chunk"].apply(lambda x: x.strip())
        df = df[df["chunk"].notna() & (df["chunk"] != "")].reset_index(drop=True)

        return df

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
        return super().randomize_samples(
            data, sample_size, products_group_size, group_columns
        )

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
        return super().generate_qa_pairs(
            randomized_samples,
            df,
            sample_size,
            products_group_size,
            group_columns,
            number_of_questions,
            qa_generator,
        )

    def add_output_sample(self, records: List[dict], chunk: str) -> None:
        super().add_output_sample(records, chunk=chunk)

    def write(self, file_path: str) -> None:
        super().write(file_path)

    def write_to_db(self, dataset_id: str, status: str, message: str) -> None:
        super().write_to_db(dataset_id, status, message)
