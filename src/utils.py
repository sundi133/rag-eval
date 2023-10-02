from processors.csv import CSVProcessor
from processors.pdf import PDFProcessor
from processors.txt import TXTProcessor
from processors.pgsql import PGSQLProcessor
from processors.ner import NERProcessor
from processors.basefile import DataProcessor
from llms import QuestionGenerator, NERGenerator
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI

llm_type_processor_mapping = {
    ".csv": CSVProcessor,
    ".txt": TXTProcessor,
    ".pdf": PDFProcessor,
    ".ner": NERProcessor,
}

llm_type_generator_mapping = {
    "text": QuestionGenerator,
    "ner": NERGenerator,
}


def create_processor(file_path: str, llm_type: str) -> DataProcessor:
    # Get the file extension
    file_extension = file_path.lower().split(".")[-1]

    # Look up the class based on the file extension
    processor_class = llm_type_processor_mapping.get(f".{file_extension}")

    if processor_class:
        # Create an instance of the chosen class
        return processor_class(file_path)
    else:
        raise ValueError(f"Unsupported file extension: {file_extension}")


def create_generator_llm(
    generator_type: str, model_name: ChatOpenAI, prompt_key: str, verbose: bool
) -> LLMChain:
    generator_class = llm_type_generator_mapping.get(generator_type)

    if generator_class:
        # Create an instance of the chosen class
        return generator_class.from_llm(model_name, prompt_key, verbose=verbose)
    else:
        raise ValueError(f"Unsupported generator type: {generator_type}")
