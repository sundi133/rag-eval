import logging
import pandas as pd
import io
import json
import argparse
from typing import List

from langchain.chains import LLMChain
from langchain.chains.base import Chain
from langchain.llms import BaseLLM
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI

from prompts import QuestionGeneratorPromptTemplate
from file_processor import FileProcessor


class QuestionGenerator(LLMChain):
    """Chain to generate questions based on the products available"""

    @classmethod
    def from_llm(cls, llm: BaseLLM, verbose: bool = True) -> LLMChain:
        """Get the response parser."""
        prompt = PromptTemplate(
            template=QuestionGeneratorPromptTemplate,
            input_variables=["products", "number_of_questions"],
        )
        return cls(prompt=prompt, llm=llm, verbose=verbose)


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
ch = logging.StreamHandler()
ch.setFormatter(formatter)
logger.addHandler(ch)


def generator(
    data_path: str,
    number_of_questions: int,
    sample_size: int,
    products_group_size: int,
    group_columns: List[str],
    output_file: str,
    model_name: str,
) -> None:
    # Initialize logger

    llm_openai_gpt4 = ChatOpenAI(
        temperature=0,
        model=model_name,
        request_timeout=120,
    )
    qa_generator = QuestionGenerator.from_llm(llm_openai_gpt4, verbose=True)

    logger.info("Starting Question Generator")

    file_processor = FileProcessor(data_path)

    df = file_processor.parse_data()
    randomized_grouping = file_processor.get_randomized_samples(
        df, sample_size, products_group_size, group_columns
    )

    # Initialize a dictionary to store questions and answers
    qa_dict = {}

    for index, group_row in randomized_grouping.iterrows():
        filtered_dataframes = []
        group_filters = []

        # Create a filter for the current group
        for column in group_columns:
            # Create a filter condition for the current column and group_row
            condition = df[column] == group_row[column]

            # Append the condition to the group_filters list
            group_filters.append(condition)

        # Combine all the filter conditions using the "&" operator
        group_filter = pd.DataFrame(group_filters).all(axis=0)

        # Filter the DataFrame based on the group criteria
        filtered_dataframes.append(df[group_filter])

        # Combine the filtered DataFrames into a single DataFrame
        combined_filtered_df = pd.concat(filtered_dataframes, ignore_index=True)

        # Initialize a CSV buffer for writing
        csv_buffer = io.StringIO()

        # Write the DataFrame to the CSV buffer
        combined_filtered_df.to_csv(csv_buffer, index=False, header=True)

        # Get the CSV string from the buffer
        products = csv_buffer.getvalue()

        # Close the buffer (optional)
        csv_buffer.close()

        qa_pair = qa_generator.run(
            products=products,
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
                    "question": record["question"],
                    "answer": record["answer"],
                }
            )
            qa_dict[record["question"]] = record["answer"]

    file_processor.write(output_file, qa_dict)

    # Log completion of Question Generator
    logger.info("Completed Question Generator")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate questions and answers dataset from provided files"
    )

    parser.add_argument("--data_path", type=str, help="Path to the input data file")
    parser.add_argument(
        "--number_of_questions", type=int, help="Number of questions to generate"
    )
    parser.add_argument(
        "--sample_size", type=int, help="Sample size for selecting groups"
    )
    parser.add_argument(
        "--products_group_size", type=int, help="Minimum number of products per group"
    )
    parser.add_argument(
        "--group_columns", type=str, nargs="+", help="Columns to group by"
    )
    parser.add_argument("--output_file", type=str, help="Path to the output file")
    parser.add_argument(
        "--model_name",
        type=str,
        default="gpt-3.5-turbo",
        help="Name of the model to use for generating questions",
    )

    args = parser.parse_args()

    data_path = args.data_path
    number_of_questions = args.number_of_questions
    sample_size = args.sample_size
    products_group_size = args.products_group_size
    output_file = args.output_file
    model_name = args.model_name
    grouped_columns = []
    if args.group_columns:
        for column in args.group_columns[0].split(","):
            grouped_columns.append(column)

    logger.info(
        {
            "message": "Arguments",
            "data_path": data_path,
            "number_of_questions": number_of_questions,
            "sample_size": sample_size,
            "products_group_size": products_group_size,
            "group_columns": grouped_columns,
            "output_file": output_file,
        }
    )
    # Call the generator function with the specified arguments
    generator(
        data_path,
        number_of_questions,
        sample_size,
        products_group_size,
        grouped_columns,
        output_file,
        model_name,
    )
