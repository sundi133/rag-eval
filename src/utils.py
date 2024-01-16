import json
import requests
import logging

from .processors.basefile import DataProcessor
from .processors.csv import CSVProcessor
from .processors.pdf import PDFProcessor
from .processors.txt import TXTProcessor
from .processors.pgsql import PGSQLProcessor
from .processors.ner import NERProcessor
from .processors.html import HTMLProcessor
from .processors.json import JSONProcessor
from .processors.basefile import DataProcessor
from .llms import DatagenQA, DatagenNER, DatagenMultiChunkQA
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from .logger import logger_setup
from typing import List

logger = logger_setup(__name__)


llm_type_processor_mapping = {
    ".csv": CSVProcessor,
    ".txt": TXTProcessor,
    ".pdf": PDFProcessor,
    ".ner": NERProcessor,
    ".html": HTMLProcessor,
    ".json": JSONProcessor,
}

llm_type_generator_mapping = {
    "text": DatagenQA,
    "text_multi_chunk": DatagenMultiChunkQA,
    "ner": DatagenNER,
}


def select_processor(
    file_path: List[str], llm_type: str, dataset_id: str
) -> DataProcessor:
    # Get the file extension
    file_extension = file_path[0].lower().split(".")[-1]

    # Look up the class based on the file extension
    if llm_type in llm_type_processor_mapping.keys():
        processor_class = llm_type_processor_mapping.get(llm_type)
    else:
        processor_class = llm_type_processor_mapping.get(f".{file_extension}")

    if processor_class:
        # Create an instance of the chosen class
        return processor_class(file_path, dataset_id=dataset_id)
    else:
        raise ValueError(f"Unsupported file extension: {file_extension}")


def select_llm(
    generator_type: str, model_name: ChatOpenAI, prompt_key: str, verbose: bool
) -> LLMChain:
    generator_class = llm_type_generator_mapping.get(generator_type)

    if generator_class:
        # Create an instance of the chosen class
        return generator_class.from_llm(model_name, prompt_key, verbose=verbose)
    else:
        raise ValueError(f"Unsupported generator type: {generator_type}")


def read_qa_data(qa_data_path: str) -> dict:
    """
    Reads a JSON file containing question-answer pairs and returns a dictionary.

    Args:
        qa_data_path (str): The path to the JSON file.

    Returns:
        dict: A dictionary containing the question-answer pairs.
    """
    try:
        with open(qa_data_path, "r") as json_file:
            qa_data = json.load(json_file)
            return qa_data
    except FileNotFoundError:
        print(f"The file '{qa_data_path}' was not found.")
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")


def read_endpoint_configurations(file_path: str) -> dict:
    """
    Reads endpoint configurations from a JSON file.

    Args:
        file_path (str): The path to the JSON file.

    Returns:
        dict: A dictionary containing the endpoint configurations.
    """
    try:
        with open(file_path, "r") as json_file:
            endpoint_configs = json.load(json_file)
            return endpoint_configs
    except FileNotFoundError:
        print(f"The file '{file_path}' was not found.")
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")


def score_answer(question: str, answer: str, endpoint_answer: str) -> float:
    """
    Calculates the score of an answer based on the similarity between the answer and the expected answer.

    Args:
        question (str): The question for which the answer is being scored.
        answer (str): The answer to be scored.
        endpoint_answer (str): The expected answer against which the answer is being scored.

    Returns:
        float: The score of the answer as a float value between 0 and 1.
    """
    pass


async def get_llm_answer(question: str, endpoint_config: str) -> str:
    """
    This function takes a question and an endpoint configuration as input and returns an answer.

    Args:
        question (str): The question to be answered.
        endpoint_config (str): The configuration for the endpoint to be used.

    Returns:
        str: The answer to the input question.
    """

    url = endpoint_config["url"]
    data = {"query": f"{question}"}
    logger.info(f"URL: {url}")
    logger.info(f"Data: {data}")

    try:
        response = requests.post(url, data=data)
        if response.status_code == 200:
            logger.info("Request successful.")
            return response.text
        else:
            logger.info(f"Request failed with status code {response.status_code}.")
            return ""
    except Exception as e:
        logger.error(f"Error getting answer from endpoint: {str(e)}")
        return ""
