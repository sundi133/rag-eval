from langchain.chains import LLMChain
from langchain.chains.base import Chain
from langchain.llms import BaseLLM
from langchain.prompts import PromptTemplate

from .prompts import QuestionGeneratorPromptTemplate


class Datagen(LLMChain):
    """Chain to generate questions based on the products available"""

    @classmethod
    def from_llm(cls, llm: BaseLLM, prompt_key: str, verbose: bool = True) -> LLMChain:
        """Get the response parser."""
        if "_csv" in prompt_key:
            prompt = PromptTemplate(
                template=QuestionGeneratorPromptTemplate.get(prompt_key),
                input_variables=[
                    "products",
                    "number_of_questions",
                    "persona",
                ],
            )
        else:
            prompt = PromptTemplate(
                template=QuestionGeneratorPromptTemplate.get(prompt_key),
                input_variables=[
                    "products",
                    "number_of_questions",
                    "persona",
                ],
            )
        return cls(prompt=prompt, llm=llm, verbose=verbose)


class DatagenMultiChunkQA(LLMChain):
    """Chain to generate questions based on the products available"""

    @classmethod
    def from_llm(cls, llm: BaseLLM, prompt_key: str, verbose: bool = True) -> LLMChain:
        """Get the response parser."""
        if "_csv" in prompt_key:
            prompt = PromptTemplate(
                template=QuestionGeneratorPromptTemplate.get(prompt_key),
                input_variables=[
                    "chunk_reference_first",
                    "chunk_reference_second",
                    "number_of_questions",
                    "schema",
                    "persona",
                ],
            )
        else:
            prompt = PromptTemplate(
                template=QuestionGeneratorPromptTemplate.get(prompt_key),
                input_variables=[
                    "chunk_reference_first",
                    "chunk_reference_second",
                    "number_of_questions",
                    "persona",
                ],
            )
        return cls(prompt=prompt, llm=llm, verbose=verbose)


class DatagenNER(LLMChain):
    """Chain to generate questions based on the products available"""

    @classmethod
    def from_llm(cls, llm: BaseLLM, prompt_key: str, verbose: bool = True) -> LLMChain:
        """Get the response parser."""
        prompt = PromptTemplate(
            template=QuestionGeneratorPromptTemplate.get(prompt_key),
            input_variables=["sample_size", "entity_name"],
        )
        return cls(prompt=prompt, llm=llm, verbose=verbose)


class DataEval(LLMChain):
    """Chain to generate questions based on the products available"""

    @classmethod
    def from_llm(cls, llm: BaseLLM, eval_prompt: str, verbose: bool = True) -> LLMChain:
        """Get the response parser."""
        prompt = PromptTemplate(
            template=eval_prompt,
            input_variables=[
                "question",
                "verified_answer",
                "app_generated_answer",
            ],
        )
        return cls(prompt=prompt, llm=llm, verbose=verbose)
