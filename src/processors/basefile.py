import os
from typing import List, Callable
from abc import ABC
from langchain.chains import LLMChain
import random
import time
import json
import pandas as pd
import logging
from datetime import datetime

try:
    from ..models import QAData, Dataset
except ImportError:
    try:
        from models import QAData, Dataset
    except ImportError:
        QAData = None
        Dataset = None

try:
    from fastapi_sqlalchemy import db
except ImportError:
    db = None

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
ch = logging.StreamHandler()
ch.setFormatter(formatter)
logger.addHandler(ch)


class DataProcessor(ABC):
    def __init__(self, data_path: List[str], dataset_id: str) -> None:
        self.data_path = data_path
        # Security fix: Use os.path.basename to remove any directory components to prevent path traversal issues
        safe_filename = os.path.basename(data_path[0]) if data_path and data_path[0] else ""  # 🔒 SECURITY FIX APPLIED
        self.file_extension = os.path.splitext(safe_filename)[-1].lower()  # 🔒 SECURITY FIX APPLIED
        self.qa_dict = {}
        self.chunk_size = 2000  # Define the chunk_size attribute here
        self.batch_size = 25
        self.chunk_reference_max_distance = 4
        self.orgId = None
        self.userId = None
        self.dataset_id = dataset_id
        self.sim_profile = None
        self.max_crawl_links = None

    def setTenant(self, tenant: str) -> None:
        self.orgId = tenant

    def setUser(self, user: str) -> None:
        self.userId = user

    def setSimProfile(self, profile: dict) -> None:
        self.sim_profile = profile
        self.chunk_size = profile["chunk_size"] if "chunk_size" in profile else 2000
        self.max_crawl_links = (
            profile["max_crawl_links"] if "max_crawl_links" in profile else None
        )

    def parse(self) -> None:
        raise NotImplementedError

    def clean_text_to_ascii(self, text):
        cleaned_text = "".join(char for char in text if ord(char) < 128)
        return cleaned_text

    def clean_text_to_ascii_df(self, text):
        return "".join(char for char in text if ord(char) < 128)

    def recursive_chunk_split(self, text):
        combined_content = self.clean_text_to_ascii(text)

        # Split by paragraphs
        paragraphs = combined_content.split("\n\n")

        # Further split each paragraph by newline, then by space
        split_content = []
        for paragraph in paragraphs:
            lines = paragraph.split("\n")
            for line in lines:
                words = line.split(" ")
                split_content.extend(words)

        # Create chunks of the desired size
        chunks = []
        current_chunk = ""
        for word in split_content:
            if len(current_chunk) + len(word) <= self.chunk_size:
                current_chunk += word + " "
            else:
                chunks.append(current_chunk.strip())
                current_chunk = word + " "

        # Add the last chunk if it's not empty
        if current_chunk:
            chunks.append(current_chunk.strip())

        # Clean up the chunks
        return [x.strip() for x in chunks]

    def randomize_samples(
        self,
        data: pd.DataFrame,
        sample_size: int,
        products_group_size: int,
        group_columns: List[str],
    ) -> pd.DataFrame:
        raise NotImplementedError

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
        raise NotImplementedError

    def add_output_sample(self, records: dict, **kwargs) -> None:
        if QAData is None or db is None:
            logger.error("QAData model or db session is not available.")
            raise ImportError("QAData model or db session is not available.")
        logger.info(
            {
                "message": "Writing generated questions to database",
            }
        )
        qadata_list = [
            QAData(
                dataset_id=self.dataset_id,
                ts=datetime.utcnow(),
                chat_messages=json.dumps(
                    {
                        "question_answer": record,
                    }
                ),
                reference_chunk=kwargs["chunk"] if "chunk" in kwargs else None,
                userid=self.userId,
                orgid=self.orgId,
            )
            for record in records
        ]
        db.session.add_all(qadata_list)
        db.session.commit()
        logger.info(
            {
                "message": "Finished writing generated questions to database",
            }
        )
        return

    def write(self, file_path: str) -> None:
        raise NotImplementedError

    def write_to_db(self, dataset_id: str, status: str, message: str) -> None:
        if Dataset is None or db is None:
            logger.error("Dataset model or db session is not available.")
            raise ImportError("Dataset model or db session is not available.")
        result = db.session.query(Dataset).filter(Dataset.id == dataset_id).first()
        if result:
            result.status = status
            result.error_msg = message
            db.session.commit()

    @staticmethod
    def retry_with_exponential_backoff(
        func: Callable,
        initial_delay: float = 1,
        exponential_base: float = 2,
        jitter: bool = True,
        max_retries: int = 3,
    ) -> Callable:
        """Retry a function with exponential backoff."""

        def wrapper(*args, **kwargs):
            num_retries = 0
            delay = initial_delay

            while True:
                try:
                    return func(*args, **kwargs)
                except (
                    TimeoutError,
                    ConnectionError,
                    ConnectionAbortedError,
                    ConnectionRefusedError,
                    ConnectionResetError,
                    json.decoder.JSONDecodeError,
                ) as e:
                    num_retries += 1

                    if num_retries > max_retries:
                        raise Exception(
                            f"Maximum number of retries ({max_retries}) exceeded."
                        )

                    delay *= exponential_base * (1 + jitter * random.random())
                    time.sleep(delay)
                except Exception as e:
                    raise e

        return wrapper