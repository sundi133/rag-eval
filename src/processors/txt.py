import os
import pandas as pd
import json
import io
import logging

from langchain.chains import LLMChain
from typing import List
from .basefile import DataProcessor


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
ch = logging.StreamHandler()
ch.setFormatter(formatter)
logger.addHandler(ch)


class TXTProcessor(DataProcessor):
    def __init__(self, data_path: str) -> None:
        super().__init__(data_path)
        self.file_extension = os.path.splitext(data_path)[-1].lower()
        self.qa_dict = {}
        self.qa_array = []
        self.chunk_size = 5000  # Define the chunk_size attribute here
        self.batch_size = 25

    def parse(self) -> pd.DataFrame:
        with open(self.data_path, "r") as f:
            content = f.read()
        chunks = [content[x : x + 5000] for x in range(0, len(content), 5000)]
        data = [x.strip() for x in chunks]

        df = pd.DataFrame({"chunk": data})
        df["chunk"] = df["chunk"].apply(lambda x: x.strip())
        df = df[df["chunk"].notna() & (df["chunk"] != "")].reset_index(drop=True)

        logger.info(
            {
                "message": "chunk[0] Parsed data",
                "chunks[0]": chunks[0],
            }
        )
        logger.info(
            {
                "message": "Parsed data",
                "data": df,
            }
        )
        return df

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
            logger.info(
                {
                    "message": "Generating question",
                    "_index": _index,
                    "group_row": group_row["chunk"],
                    "length": len(group_row["chunk"]),
                }
            )
            try:
                # conver each row to a pd dataframe
                filtered_dataframes = []
                row_df = pd.DataFrame([group_row])
                filtered_dataframes.append(row_df)

                # Combine the filtered DataFrames into a single DataFrame
                combined_filtered_df = pd.concat(filtered_dataframes, ignore_index=True)

                # Initialize a CSV buffer for writing
                csv_buffer = io.StringIO()

                # Write the DataFrame to the CSV buffer
                combined_filtered_df.to_csv(csv_buffer, index=False, header=False)

                # Get the CSV string from the buffer
                records = csv_buffer.getvalue()

                # Close the buffer (optional)
                csv_buffer.close()

                if len(records) < 100:
                    continue

                if (
                    number_of_questions > 25
                ):  # too many questions might cause token limit error
                    number_of_questions = self.batch_size
                qa_pair = qa_generator.run(
                    products=records,
                    number_of_questions=number_of_questions,
                )

                # Split questions by newline and process each question
                question_array = json.loads(qa_pair)
                logger.info(
                    {
                        "message": "Generated question & answer pair length",
                        "questions": len(question_array),
                    }
                )
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

            except Exception as e:
                logger.error(
                    {
                        "message": "Error generating question",
                        "error": str(e),
                    }
                )
                continue
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
