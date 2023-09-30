from processors.basefile import FileProcessor
import os
import pandas as pd
import os
import json
from typing import List
from abc import ABC, abstractmethod

class CSVProcessor(FileProcessor):
    def __init__(self, data_path: str) -> None:
        super().__init__(data_path)
        self.file_extension = os.path.splitext(data_path)[-1].lower()
        self.data = self.parse()
    
    def parse(self)-> pd.DataFrame:
        return pd.read_csv(self.data_path, index_col=False)

    def get_randomized_samples(
        self,
        data: pd.DataFrame,
        sample_size: int,
        products_group_size: int,
        group_columns: List[str],
    ) -> pd.DataFrame:
        df = data

        # Group the group_columns
        grouped = df.groupby(group_columns)

        # Define a filter function to check if the group has at least 'products_group_size' products
        def filter_groups(group):
            return len(group) >= products_group_size

        # Apply the filter function to each group and concatenate the results
        filtered_df = grouped.filter(filter_groups)

        # Calculate group counts after filtering
        group_counts = (
            filtered_df.groupby(group_columns).size().reset_index(name="count")
        )

        # Filter groups with at least 'products_group_size' products
        group_counts_filter = group_counts[group_counts["count"] >= products_group_size]

        # Randomly select 'sample_size' groups
        randomized_grouping = group_counts_filter.sample(n=sample_size, random_state=42)
        return randomized_grouping

    def write(self, file_path: str, data: json) -> None:
        with open(file_path, "w") as output_file:
            # Write each key-value pair as a separate JSON object per line
            for key, value in data.items():
                json_record = json.dumps({"question": key, "answer": value})
                output_file.write(json_record + "\n")
