from processors.csv import CSVProcessor
from processors.pdf import PDFProcessor
from processors.txt import TXTProcessor
from processors.pgsql import PGSQLProcessor

file_extension_mapping = {
    ".csv": CSVProcessor,
    ".txt": TXTProcessor,
    ".pdf": PDFProcessor,
}


def create_processor(file_path):
    # Get the file extension
    file_extension = file_path.lower().split(".")[-1]

    # Look up the class based on the file extension
    processor_class = file_extension_mapping.get(f".{file_extension}")

    if processor_class:
        # Create an instance of the chosen class
        return processor_class(file_path)
    else:
        raise ValueError(f"Unsupported file extension: {file_extension}")
