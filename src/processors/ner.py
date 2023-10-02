from processors.basefile import DataProcessor
import os
import pandas as pd
import random
import json
import io
import logging
from typing import List
from langchain.chains import LLMChain

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
ch = logging.StreamHandler()
ch.setFormatter(formatter)
logger.addHandler(ch)


class NERProcessor(DataProcessor):
    def __init__(self, data_path: str) -> None:
        super().__init__(data_path)
        self.file_extension = os.path.splitext(data_path)[-1].lower()
        self.qa_dict = {}
        self.qa_dict["training_data"] = []
        self.entities_json = {}

    def set_entity(self, entities_file) -> None:
        with open(entities_file, "r") as json_file:
            self.entities_json = json.load(json_file)
        self.entity_name = self.entities_json["name"]

    def parse(self) -> pd.DataFrame:
        # Open the input file containing sentences
        with open(self.data_path, "r") as input_file:
            sentences = input_file.readlines()

        # Extract the key-value pairs
        key_values = self.entities_json["key_values"]

        modified_df = []
        for chosen_key in list(key_values.keys()):
            for sentence in sentences:
                replacements = key_values.get(chosen_key, [])
                if replacements:
                    replacement_value = random.choice(replacements)
                else:
                    continue
                if chosen_key in sentence:
                    modified_sentence = sentence.replace(
                        f"{{{chosen_key}}}", replacement_value
                    )

                modified_df.append(modified_sentence)
        outdf = pd.DataFrame(modified_df, columns=["sentence"])
        return outdf

    def get_randomized_samples(
        self,
        data: pd.DataFrame,
        sample_size: int,
        products_group_size: int,
        group_columns: List[str],
    ) -> pd.DataFrame:
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
        # Initialize a CSV buffer for writing
        csv_buffer = io.StringIO()

        # Write the DataFrame to the CSV buffer
        randomized_samples.to_csv(csv_buffer, index=False, header=True)

        # Get the CSV string from the buffer
        records = csv_buffer.getvalue()

        # Close the buffer (optional)
        csv_buffer.close()

        qa_pair = qa_generator.run(
            sentences=records,
            entity_name=self.entity_name,
        )

        # Log generated questions
        logger.info(
            {
                "message": "Generated NER training dataset",
                "data": qa_pair,
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
                }
            )
            self.add_output_sample(record)

        return self.qa_dict

    def add_output_sample(self, record: json) -> None:
        training_data = self.qa_dict["training_data"]
        training_data.append(record)
        self.qa_dict["training_data"] = training_data

    def write(self, file_path: str, qa_pairs: json) -> None:
        with open(file_path, "w") as output_file:
            # Write each key-value pair as a separate JSON object per line
            for _key, values in qa_pairs.items():
                for value in values:
                    json_data = json.dumps(value, separators=(",", ":"))
                    output_file.write(str(json_data) + "\n")
