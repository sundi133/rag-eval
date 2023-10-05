import os
import pandas as pd
import os
import json
import requests

from urllib.parse import urljoin
from typing import List
from bs4 import BeautifulSoup
from processors.basefile import DataProcessor


class HTMLProcessor(DataProcessor):
    def __init__(self, data_path: str) -> None:
        super().__init__(data_path)
        self.file_extension = os.path.splitext(data_path)[-1].lower()

    # Function to extract paragraphs within h1 or h2 headers from a webpage
    def extract_paragraphs_from_headers(self, url):
        try:
            response = requests.get(url)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            # Extract paragraphs within h1 and h2 headers along with URL separators
            extracted_paragraphs = []

            for header_level in ["h1", "h2"]:
                header_elements = soup.find_all(header_level)
                for header in header_elements:
                    paragraphs = header.find_all_next("p")
                    for paragraph in paragraphs:
                        # Add the URL as a separator before each paragraph
                        extracted_paragraphs.append(f"{url}, {paragraph.text}")

            return extracted_paragraphs
        except Exception as e:
            print(f"Error extracting content from {url}: {str(e)}")
            return []

    # Function to crawl multiple URLs up to a specified depth and store results in a DataFrame
    def crawl_urls(self, urls, depth):
        data = []

        if depth == 0:
            return data

        for url in urls:
            print(f"Crawling {url}, Depth: {depth}")
            extracted_paragraphs = self.extract_paragraphs_from_headers(url)
            if extracted_paragraphs:
                data.extend(extracted_paragraphs)

            try:
                response = requests.get(url)
                response.raise_for_status()

                soup = BeautifulSoup(response.text, "html.parser")

                # Find and follow links on the page
                links = soup.find_all("a", href=True)
                next_urls = [urljoin(url, link["href"]) for link in links]
                data.extend(self.crawl_urls(next_urls, depth - 1))
            except Exception as e:
                print(f"Error crawling {url}: {str(e)}")

        return data

    def parse(self) -> pd.DataFrame:
        crawling_depth = 4
        crawled_data = self.crawl_url(self.data_path, crawling_depth)
        return pd.DataFrame(crawled_data, columns=["url", "text"])

    def get_randomized_samples(
        self,
        data: pd.DataFrame,
        sample_size: int,
        products_group_size: int,
        group_columns: List[str],
    ) -> pd.DataFrame:
        return data.sample(n=sample_size, random_state=42)

    def write(self, file_path: str, qa_pairs: json) -> None:
        pass
