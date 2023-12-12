import os
import pandas as pd
import json
import requests
import io
import logging
import numpy as np

from langchain.chains import LLMChain
from urllib.parse import urljoin
from typing import List
from bs4 import BeautifulSoup
from .basefile import DataProcessor

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
ch = logging.StreamHandler()
ch.setFormatter(formatter)
logger.addHandler(ch)


class HTMLProcessor(DataProcessor):
    def __init__(self, data_path: str) -> None:
        super().__init__(data_path)
        self.file_extension = os.path.splitext(data_path)[-1].lower()
        self.visited = {}
        self.data = []
        self.depth = 2
        self.qa_dict = {}
        self.qa_array = []
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
        }
        self.batch_size = 25

    def set_depth(self, depth: int) -> None:
        self.depth = depth

    def extract_paragraphs_from_headers(self, url):
        if url in self.visited:
            return
        try:
            response = requests.get(url, headers=self.headers)
            self.visited[url] = True
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            page_title = soup.title.string if soup.title else "No title"

            extracted_paragraphs = []

            paragraphs = soup.find_all("p")
            if paragraphs:
                for paragraph in paragraphs:
                    extracted_paragraphs.append((url, page_title, paragraph.text))
            return extracted_paragraphs
        except Exception as e:
            print(f"Error extracting content from {url}: {str(e)}")
            return []

    def crawl_url(self, starting_url, url, depth):
        if depth == 0 or not url.startswith(starting_url):
            return

        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                extracted_paragraphs = self.extract_paragraphs_from_headers(url)
                if extracted_paragraphs:
                    self.data.extend(extracted_paragraphs)

                # Extract and follow links on the page
                soup = BeautifulSoup(response.text, "html.parser")
                links = soup.find_all("a")
                for link in links:
                    next_url = urljoin(url, link.get("href"))
                    self.crawl_url(starting_url, next_url, depth - 1)
        except Exception as e:
            print(f"Error crawling {url}: {str(e)}")

    def split_text(self, text, max_words=2000):
        words = text.split()
        num_chunks = len(words) // max_words
        chunks = np.array_split(words, num_chunks + 1)
        return [" ".join(chunk) for chunk in chunks]

    def parse(self) -> pd.DataFrame:
        crawling_depth = self.depth
        self.crawl_url(self.data_path, self.data_path, crawling_depth)
        # group by url and concatenate the text and title
        df = pd.DataFrame(self.data, columns=["url", "title", "text"])
        grouped_df = df.groupby(["url", "title"])["text"].apply(" ".join).reset_index()
        # Apply the split_text function to each row in the grouped DataFrame
        grouped_df["text"] = grouped_df["text"].apply(
            lambda text: self.split_text(text)
        )
        flattened_df = grouped_df.explode("text").reset_index(drop=True)
        return flattened_df

    def get_randomized_samples(
        self,
        data: pd.DataFrame,
        sample_size: int,
        products_group_size: int,
        group_columns: List[str],
    ) -> pd.DataFrame:
        if sample_size > data.shape[0]:
            sample_size = data.shape[0]
        return data.sample(n=sample_size, random_state=42)

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

            logger.info(
                {
                    "message": "Generating question",
                    "group_row": _index,
                    "records": records,
                }
            )

            if number_of_questions > 25:
                number_of_questions = self.batch_size

            qa_pair = self.completions_with_backoff(
                qa_generator, records=records, number_of_questions=number_of_questions
            )

            logger.info(
                {
                    "message": "Generated question",
                    "qa_pair": qa_pair,
                }
            )
            try:
                # Split questions by newline and process each question
                question_array = json.loads(qa_pair)
                for record in question_array:
                    record["url"] = group_row["url"]
                    # Log each generated question
                    logger.info(
                        {
                            "message": "Generated question",
                            "question_answer": record,
                        }
                    )
                    self.add_output_sample(record)
            except Exception as e:
                logger.info(
                    {
                        "log_type": "error",
                        "message": "Error generating question",
                        "exception": str(e),
                    }
                )
        return self.qa_dict

    def add_output_sample(self, record: json) -> None:
        self.qa_array.append(
            {
                "question": record["question"],
                "answer": record["answer"],
                "url": record["url"],
            }
        )

    @staticmethod
    @DataProcessor.retry_with_exponential_backoff
    def completions_with_backoff(
        qa_generator: LLMChain, records: str, number_of_questions: int
    ):
        return qa_generator.run(
            products=records,
            number_of_questions=number_of_questions,
        )

    def write(self, file_path: str) -> None:
        sorted_data = sorted(self.qa_array, key=lambda x: x["url"])
        with open(file_path, "w") as output_file:
            json.dump(sorted_data, output_file, indent=4)
