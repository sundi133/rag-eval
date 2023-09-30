import pandas as pd
import os
import json
from typing import List

# TODO - Implement proper abstractions and oo design with logging
# TODO - Implement proper error handling


class FileProcessor:
    def __init__(self, data_path: str) -> None:
        self.data_path = data_path
        self.file_extension = os.path.splitext(data_path)[-1].lower()

    def read_csv(self) -> pd.DataFrame:
        return pd.read_csv(self.data_path, index_col=False)

    def read_txt(self) -> pd.DataFrame:
        pass  # TODO: Implement

    def read_pdf(self) -> pd.DataFrame:
        pass  # TODO: Implement

    def parse_data(self) -> pd.DataFrame:
        if self.file_extension == ".csv":
            return self.read_csv()
        elif self.file_extension == ".txt":
            return self.read_txt()
        elif self.file_extension == ".pdf":
            return self.read_pdf()
        else:
            return None

    def randomize_csv(
        self,
        data: pd.DataFrame,
        sample_size: int,
        products_group_size: int,
        group_columns: List[str],
    ) -> pd.DataFrame:
        df = self.parse_data()

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

    def randomize_txt(
        self,
        data: pd.DataFrame,
        sample_size: int,
        products_group_size: int,
        group_columns: List[str],
    ) -> pd.DataFrame:
        pass

    def randomize_pdf(
        self,
        data: pd.DataFrame,
        sample_size: int,
        products_group_size: int,
        group_columns: List[str],
    ) -> pd.DataFrame:
        pass

    def get_randomized_samples(
        self,
        data: pd.DataFrame,
        sample_size: int,
        products_group_size: int,
        group_columns: List[str],
    ) -> pd.DataFrame:
        if self.file_extension == ".csv":
            return self.randomize_csv(
                data, sample_size, products_group_size, group_columns
            )
        elif self.file_extension == ".txt":
            return self.randomize_txt(
                data, sample_size, products_group_size, group_columns
            )
        elif self.file_extension == ".pdf":
            return self.randomize_pdf(
                data, sample_size, products_group_size, group_columns
            )
        else:
            return None

    def write(self, file_path: str, data: json) -> None:
        with open(file_path, "w") as output_file:
            # Write each key-value pair as a separate JSON object per line
            for key, value in data.items():
                json_record = json.dumps({key: value})
                output_file.write(json_record + "\n")
