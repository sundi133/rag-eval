import logging
import pandas as pd
import json
import argparse
from typing import List

from langchain.chains import LLMChain
from langchain.chains.base import Chain
from langchain.llms import BaseLLM
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI

from utils import create_processor, create_processor_llm
from llms import QuestionGenerator

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
    prompt_key: str,
    llm_type: str,
    generator_type: str,
    metadata_path: str,
    crawl_depth: int,
) -> None:
    """
    Generate questions and answers or training dataset from provided files
    """

    llm_openai_gpt4 = ChatOpenAI(
        temperature=0,
        model=model_name,
        request_timeout=120,
    )

    logger.info("Starting Question Generator")

    qa_generator = create_processor_llm(
        generator_type, llm_openai_gpt4, prompt_key, verbose=True
    )

    data_processor = create_processor(data_path, llm_type)

    if llm_type == "ner":
        data_processor.set_entity(metadata_path)
    if llm_type == ".html":
        data_processor.set_depth(crawl_depth)

    df = data_processor.parse()

    randomized_samples = data_processor.get_randomized_samples(
        df, sample_size, products_group_size, group_columns
    )

    qa_pairs = data_processor.generate_qa_pairs(
        randomized_samples,
        df,
        sample_size,
        products_group_size,
        group_columns,
        number_of_questions,
        qa_generator,
    )

    data_processor.write(output_file)

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
        "--products_group_size",
        type=int,
        default=3,
        help="Minimum number of products per group",
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
    parser.add_argument(
        "--prompt_key",
        type=str,
        default="prompt_key_csv",
        help="Name of the prompt key to use for generating questions",
    )
    parser.add_argument(
        "--llm_type",
        type=str,
        default="text",
        help="Type of LLM to use for generating questions",
    )
    parser.add_argument(
        "--generator_type",
        type=str,
        default="text",
        help="Type of generator to use for generating questions",
    )
    parser.add_argument(
        "--metadata_path",
        type=str,
        default="",
        help="Path to the metadata file",
    )
    parser.add_argument(
        "--crawl_depth",
        type=int,
        default=2,
        help="Depth to crawl",
    )

    args = parser.parse_args()

    data_path = args.data_path
    number_of_questions = args.number_of_questions
    sample_size = args.sample_size
    products_group_size = args.products_group_size
    output_file = args.output_file
    model_name = args.model_name
    prompt_key_csv = args.prompt_key
    llm_type = args.llm_type
    generator_type = args.generator_type
    metadata_path = args.metadata_path
    crawl_depth = args.crawl_depth
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
            "model_name": model_name,
            "prompt_key": prompt_key_csv,
            "llm_type": llm_type,
            "generator_type": generator_type,
            "metadata_path": metadata_path,
            "crawl_depth": crawl_depth,
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
        prompt_key_csv,
        llm_type,
        generator_type,
        metadata_path,
        crawl_depth,
    )
