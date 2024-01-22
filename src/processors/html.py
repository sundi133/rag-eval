import os
import pandas as pd
import json
import io
import logging
import random
import time
import numpy as np
import requests
import tldextract
import re

from langchain.chains import LLMChain
from typing import List
from .basefile import DataProcessor
from ..models import QAData
from sqlalchemy.orm import Session
from datetime import datetime
from fastapi_sqlalchemy import DBSessionMiddleware, db
from bs4 import BeautifulSoup
from urllib.parse import urljoin

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
ch = logging.StreamHandler()
ch.setFormatter(formatter)
logger.addHandler(ch)


class HTMLProcessor(DataProcessor):
    def __init__(self, data_path: List[str], dataset_id: str) -> None:
        super().__init__(data_path, dataset_id)
        self.visited = {}
        self.to_be_visited = {}
        self.data = []
        self.depth = 2
        self.qa_dict = {}
        self.qa_array = []
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
        }
        self.batch_size = 25
        self.chunk_size = 2000
        self.chunk_reference_max_distance = 4

    def setTenant(self, tenant: str) -> None:
        super().setTenant(tenant)

    def setUser(self, user: str) -> None:
        super().setUser(user)

    def setSimProfile(self, profile: dict) -> None:
        super().setSimProfile(profile)

    def set_depth(self, depth: int) -> None:
        self.depth = depth

    def extract_content(self, url, html):
        if url in self.visited:
            return
        try:
            self.visited[url] = True
            soup = BeautifulSoup(html, "html.parser")

            page_title = soup.title.string if soup.title else "No title"

            extracted_paragraphs = []

            paragraphs = soup.find_all("p")
            if paragraphs:
                for paragraph in paragraphs:
                    extracted_paragraphs.append((url, page_title, paragraph.text))

            # Extract text from other common text-containing HTML elements (e.g., <div>, <span>, <h1>, etc.)
            other_elements = soup.find_all(
                ["div", "span", "h1", "h2", "h3", "h4", "h5", "h6", "li", "a", "td"]
            )
            if other_elements:
                for element in other_elements:
                    extracted_paragraphs.append((url, page_title, element.text))

            return extracted_paragraphs
        except Exception as e:
            print(f"Error extracting content from {url}: {str(e)}")
            return []

    def get_base_domain(self, url):
        extracted_info = tldextract.extract(url)
        base_domain = f"{extracted_info.domain}.{extracted_info.suffix}"
        return base_domain

    def crawl_url(self, starting_url, url, depth):
        if (
            url.endswith(".pdf")
            or url.endswith(".docx")
            or url.endswith(".doc")
            or url.endswith(".ppt")
            or url.endswith(".pptx")
            or url.endswith(".xls")
            or url.endswith(".xlsx")
            or url.endswith(".csv")
            or url.endswith(".txt")
            or url.endswith(".rtf")
            or url.endswith(".odt")
            or url.endswith(".ods")
            or url.endswith(".odp")
            or url.endswith(".odg")
            or url.endswith(".odf")
            or url.endswith(".odc")
            or url.endswith(".odb")
            or url.endswith(".tgz")
            or url.endswith(".gz")
            or url.endswith(".zip")
            or url.endswith(".tar")
            or url.endswith(".rar")
            or url.endswith(".7z")
            or url.endswith(".bz2")
            or url.endswith(".xz")
            or url.endswith(".lz")
            or url.endswith(".lzma")
            or url.endswith(".lzo")
            or url.endswith(".z")
            or url.endswith(".Z")
            or url.endswith(".lz4")
            or url.endswith(".arj")
            or url.endswith(".cab")
            or url.endswith(".deb")
            or url.endswith(".pkg")
            or url.endswith(".rpm")
            or url.endswith(".sit")
            or url.endswith(".sitx")
            or url.endswith(".gz")
            or url.endswith(".tgz")
            or url.endswith(".bz2")
            or url.endswith(".tbz2")
            or url.endswith(".zip")
            or url.endswith(".zipx")
            or url.endswith(".tar")
            or url.endswith(".gz")
            or url.endswith(".tgz")
            or url.endswith(".bz2")
            or url.endswith(".tbz2")
            or url.endswith(".zip")
            or url.endswith(".tar")
            or url.endswith(".gz")
            or url.endswith(".tgz")
            or url.endswith(".bz2")
            or url.endswith(".tbz2")
            or url.endswith(".zip")
            or url.endswith(".tar")
            or url.endswith(".gz")
            or url.endswith(".tgz")
            or url.endswith(".bz2")
            or url.endswith(".tbz2")
            or url.endswith(".zip")
            or url.endswith(".tar")
            or url.endswith(".gz")
            or url.endswith(".tgz")
            or url.endswith(".bz2")
            or url.endswith(".tbz2")
            or url.endswith(".zip")
            or url.endswith(".tar")
            or url.endswith(".gz")
            or url.endswith(".tgz")
            or url.endswith(".bz2")
            or url.endswith(".tbz2")
            or url.endswith(".zip")
            or url.endswith(".tar")
            or url.endswith(".gz")
            or url.endswith(".tgz")
            or url.endswith(".bz2")
            or url.endswith(".tbz2")
        ):
            return

        if (
            depth == 0
            or self.get_base_domain(starting_url) != self.get_base_domain(url)
            or url in self.visited
        ):
            return
        if not url.startswith("http") or not url.startswith("https"):
            return

        if len(self.to_be_visited) > self.max_crawl_links:
            return
        try:
            response = requests.get(url, headers=self.headers)
            logger.info(
                {
                    "message": "Crawling URL",
                    "url": url,
                    "response": response.status_code,
                }
            )
            if response.status_code == 200:
                extracted_paragraphs = self.extract_content(url, response.text)
                if extracted_paragraphs:
                    self.data.extend(extracted_paragraphs)

                # Extract and follow links on the page
                soup = BeautifulSoup(response.text, "html.parser")
                links = soup.find_all("a")
                for link in links:
                    if link.get("href"):
                        if link.get("href").startswith("http") or link.get(
                            "href"
                        ).startswith("https"):
                            next_url = link.get("href")

                            self.crawl_url(starting_url, next_url, depth - 1)
                        else:
                            next_url = urljoin(url, link.get("href"))

                            self.crawl_url(starting_url, next_url, depth - 1)

        except Exception as e:
            print(f"Error crawling {url}: {str(e)}")

    def process_text(self, text_group):
        return " ".join(text_group.values)

    def process_df(self, df):
        # Group by URL and title
        grouped_df = (
            df.groupby(["url", "title"])
            .apply(
                lambda group: pd.DataFrame(
                    {
                        "url": group["url"],
                        "title": group["title"],
                        "text_chunks": self.process_text(group["text"]),
                    }
                )
            )
            .reset_index(drop=True)
            .explode("text_chunks")
            .drop_duplicates()
        )

        return grouped_df

    def parse(self) -> pd.DataFrame:
        crawling_depth = self.depth

        combined_data = []

        for data in self.data_path:
            # Assuming crawl_url returns a list of dictionaries containing data
            self.crawl_url(data, data, depth=crawling_depth)
            df = pd.DataFrame(self.data, columns=["url", "title", "text"])
            self.data = []
            combined_data.append(df)

        # Create a DataFrame from the combined data
        df = pd.concat(combined_data, ignore_index=True)

        df = self.process_df(df).reset_index(drop=True)
        df = df.applymap(self.clean_text_to_ascii_df)

        logger.info(
            {
                "message": "Deduped data",
                "df": df.shape,
            }
        )
        return df

    def randomize_samples(
        self,
        data: pd.DataFrame,
        sample_size: int,
        products_group_size: int,
        group_columns: List[str],
    ) -> pd.DataFrame:
        if sample_size > data.shape[0]:
            sample_size = data.shape[0]
        return data.sample(n=sample_size, random_state=42).reset_index(drop=True)

    def chunk_text(self, text, chunk_size=1000):
        words = re.findall(r"\S+", text)
        chunks = [words[i : i + chunk_size] for i in range(0, len(words), chunk_size)]
        return [" ".join(chunk) for chunk in chunks]

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
            # conver each row to a pd dataframe
            filtered_dataframes = []
            row_df = pd.DataFrame([group_row])
            filtered_dataframes.append(row_df)

            # Combine the filtered DataFrames into a single DataFrame
            combined_filtered_df = pd.concat(filtered_dataframes, ignore_index=True)

            # Initialize a CSV buffer for writing
            csv_buffer = io.StringIO()

            # Write the DataFrame to the CSV buffer
            combined_filtered_df.to_csv(csv_buffer, index=False, header=True)

            # Get the CSV string from the buffer
            records = csv_buffer.getvalue()

            # Close the buffer (optional)
            csv_buffer.close()

            text_chunks = self.chunk_text(records, chunk_size=self.chunk_size)

            for text_chunk in text_chunks:
                if len(text_chunk) < 64:
                    continue

                if number_of_questions > self.batch_size:
                    number_of_questions = self.batch_size

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
                    if len(window_indices) == 0:
                        continue

                    desired_index = window_indices[-1]
                    row_content = randomized_samples.iloc[desired_index]
                    row_df = pd.DataFrame([row_content])

                    # Convert DataFrame to a CSV-formatted string in memory
                    csv_string_io = io.StringIO()
                    row_df.to_csv(csv_string_io, index=False)
                    row_data = csv_string_io.getvalue()

                    chunk_references_second = self.chunk_text(
                        row_data, chunk_size=self.chunk_size
                    )
                    chunk_reference_second = chunk_references_second[
                        np.random.randint(0, len(chunk_references_second))
                    ]

                    qa_pair = qa_generator.run(
                        chunk_reference_first=text_chunk,
                        chunk_reference_second=chunk_reference_second,
                        number_of_questions=number_of_questions,
                        persona=self.sim_profile["persona"],
                    )
                    records = (
                        text_chunk
                        + "\n\n"
                        + "Distant reference chunk: "
                        + chunk_reference_second
                    )
                else:
                    qa_pair = qa_generator.run(
                        products=text_chunk,
                        number_of_questions=number_of_questions,
                        persona=self.sim_profile["persona"],
                    )

                    records = text_chunk

                # Log generated questions

                # Split questions by newline and process each question
                question_array = json.loads(qa_pair)
                qadata = []
                for record in question_array:
                    qadata.append(record)
                self.add_output_sample(qadata, chunk=records)

        return self.qa_dict

    def add_output_sample(self, records: List[dict], chunk: str) -> None:
        super().add_output_sample(records, chunk=chunk)

    def write(self, file_path: str) -> None:
        pass

    def write_to_db(self, dataset_id: str, status: str, message: str) -> None:
        super().write_to_db(dataset_id, status, message)

    @staticmethod
    @DataProcessor.retry_with_exponential_backoff
    def completions_with_backoff(
        qa_generator: LLMChain, records: str, number_of_questions: int
    ):
        return qa_generator.run(
            products=records,
            number_of_questions=number_of_questions,
        )
