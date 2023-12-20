import pandas as pd
import os
import io
import logging
import json
from typing import List
from langchain.chains import LLMChain
from .basefile import DataProcessor

# TODO move to central logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
ch = logging.StreamHandler()
ch.setFormatter(formatter)
logger.addHandler(ch)


class CSVProcessor(DataProcessor):
    def __init__(self, data_path: str) -> None:
        super().__init__(data_path)
        self.file_extension = os.path.splitext(data_path)[-1].lower()
        self.data = self.parse()
        self.qa_dict = {}
        self.qa_array = []
        self.schema = None
        self.batch_size = 25
        self.chunk_size = 2000

    def parse(self) -> pd.DataFrame:
        df = pd.read_csv(self.data_path, index_col=False)
        self.schema = list(df.columns)
        df.fillna("", inplace=True)
        return df

    def randomize_samples(
        self,
        df: pd.DataFrame,
        sample_size: int,
        products_group_size: int,
        group_columns: List[str],
    ) -> pd.DataFrame:
        logger.info(
            {
                "message": "Getting randomized samples",
                "df": df.shape,
                "sample_size": sample_size,
                "products_group_size": products_group_size,
                "group_columns": group_columns,
            }
        )
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

        # Calculate group counts after filtering
        group_counts = (
            filtered_df.groupby(group_columns).size().reset_index(name="count")
        )
        logger.info(
            {
                "message": "Filtered groups",
                "group_counts": group_counts.head(),
                "group_counts_shape": group_counts.shape,
            }
        )
        # Filter groups with at least 'products_group_size' products
        group_counts_filter = group_counts[group_counts["count"] >= products_group_size]

        logger.info(
            {
                "message": "Filtered groups",
                "group_counts_filter": group_counts_filter.shape,
                "group_counts_filter_head": group_counts_filter.head(),
            }
        )
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
        logger.info(
            {
                "message": "Generating question & answer pairs",
                "randomized_samples": randomized_samples.shape,
            }
        )
        for _index, group_row in randomized_samples.iterrows():
            filtered_dataframes = []
            group_filters = []
            logger.info(
                {
                    "message": "Generating question",
                    "_index": _index,
                    "group_columns": group_columns,
                    "group_row": group_row.shape,
                    "df": df.shape,
                    "df_columns": df.columns,
                }
            )
            logger.info("****")
            logger.info(group_row.head())
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

            if number_of_questions > 25:
                number_of_questions = self.batch_size

            if len(records) < 20:
                continue

            logger.info(
                {
                    "message": "Generated question",
                    "group_row": _index,
                    "records": records,
                    "records length": len(records),
                }
            )

            if len(records) > self.chunk_size:
                records = records[0 : self.chunk_size]

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

                row_df = pd.DataFrame([row_content])

                # Convert DataFrame to a CSV-formatted string in memory
                csv_string_io = io.StringIO()
                row_df.to_csv(csv_string_io, index=False)
                chunk_reference_second = csv_string_io.getvalue()

                qa_pair = qa_generator.run(
                    chunk_reference_first=records,
                    chunk_reference_second=chunk_reference_second,
                    number_of_questions=number_of_questions,
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
                )

            # Log generated questions
            logger.info(
                {
                    "message": "Generated question & answer pair",
                    "questions": qa_pair,
                }
            )

            # Split questions by newline and process each question
            question_array = json.loads(qa_pair)

            for record in question_array:
                # Log each generated question
                logger.info(
                    {
                        "message": "Generated question",
                        "question_answer": record,
                        "reference": records,
                    }
                )
                self.add_output_sample(record, chunk=records)
        return self.qa_dict

    def add_output_sample(self, record: json, chunk: str) -> None:
        self.qa_array.append(
            {
                "question_answer": record,
                "reference": chunk,
            }
        )

    def write(self, file_path: str) -> None:
        logger.info(
            {
                "message": "Writing generated questions to file",
                "file_path": file_path,
            }
        )
        with open(file_path, "w") as output_file:
            json.dump(self.qa_array, output_file, indent=4)
