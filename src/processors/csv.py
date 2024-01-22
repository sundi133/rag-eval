import os
import pandas as pd
import json
import io
import logging
import random
import time
import numpy as np

from langchain.chains import LLMChain
from typing import List
from .basefile import DataProcessor
from ..models import QAData
from sqlalchemy.orm import Session
from datetime import datetime
from fastapi_sqlalchemy import DBSessionMiddleware, db


# TODO move to central logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
ch = logging.StreamHandler()
ch.setFormatter(formatter)
logger.addHandler(ch)


class CSVProcessor(DataProcessor):
    def __init__(self, data_path: List[str], dataset_id: str) -> None:
        super().__init__(data_path, dataset_id)
        self.qa_dict = {}
        self.qa_array = []
        self.schema = None
        self.batch_size = 25
        self.chunk_size = 2000

    def setTenant(self, tenant: str) -> None:
        super().setTenant(tenant)

    def setUser(self, user: str) -> None:
        super().setUser(user)

    def setSimProfile(self, profile: dict) -> None:
        super().setSimProfile(profile)

    def parse(self) -> pd.DataFrame:
        combined_df = pd.DataFrame()
        for file_path in self.data_path:
            # Read each CSV file into a DataFrame
            df = pd.read_csv(file_path, index_col=False)
            df.fillna("", inplace=True)
            self.schema = list(df.columns)
            combined_df = pd.concat([combined_df, df], ignore_index=True)
        combined_df = combined_df.applymap(self.clean_text_to_ascii_df)
        return combined_df

    def randomize_samples(
        self,
        df: pd.DataFrame,
        sample_size: int,
        products_group_size: int,
        group_columns: List[str],
    ) -> pd.DataFrame:
        if len(group_columns) == 0:
            if sample_size > df.shape[0]:
                sample_size = df.shape[0]
            return df.sample(n=sample_size, random_state=42)
        # Group the group_columns
        grouped = df.groupby(group_columns)

        # Define a filter function to check if the group has at least 'products_group_size' products
        def filter_groups(group):
            return len(group) >= products_group_size

        # Apply the filter function to each group and concatenate the results
        filtered_df = grouped.filter(filter_groups)

        # Calculate group csounts after filtering
        group_counts = (
            filtered_df.groupby(group_columns).size().reset_index(name="count")
        )

        # Filter groups with at least 'products_group_size' products
        group_counts_filter = group_counts[group_counts["count"] >= products_group_size]

        # Randomly select 'sample_size' groups
        if sample_size > group_counts_filter.shape[0]:
            sample_size = group_counts_filter.shape[0]

        randomized_grouping = group_counts_filter.sample(n=sample_size, random_state=42)
        return randomized_grouping

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
            filtered_dataframes = []
            group_filters = []

            # Create a filter for the current group
            for column in group_columns:
                # Create a filter condition for the current column and group_row
                condition = df[column] == group_row[column]

                # Append the condition to the group_filters list
                group_filters.append(condition)

            # Combine all the filter conditions using the "&" operator
            if group_filters:
                group_filter = pd.DataFrame(group_filters).all(axis=0)
            else:
                # Handle the case where there are no conditions in group_filters
                group_filter = pd.Series(True, index=df.index)

            filtered_df = df[group_filter]

            filtered_dataframes.append(filtered_df)

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

            # too many questions will cause the model to pollute the answer
            if number_of_questions > 25:
                number_of_questions = self.batch_size

            # skip if the chunk is too small
            if len(records) < 20:
                continue

            if len(records) > self.chunk_size:
                records = records[0 : self.chunk_size]

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

                row_df = pd.DataFrame([row_content])

                csv_string_io = io.StringIO()
                row_df.to_csv(csv_string_io, index=False)
                chunk_reference_second = csv_string_io.getvalue()

                qa_pair = qa_generator.run(
                    chunk_reference_first=records,
                    chunk_reference_second=chunk_reference_second,
                    number_of_questions=number_of_questions,
                    schema=self.schema,
                    persona=self.sim_profile["persona"],
                )
                records = (
                    records
                    + "\n\n"
                    + "Distant reference chunk: "
                    + chunk_reference_second
                )
            else:
                qa_pair = qa_generator.run(
                    products=records,
                    number_of_questions=number_of_questions,
                    schema=self.schema,
                    persona=self.sim_profile["persona"],
                )

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
