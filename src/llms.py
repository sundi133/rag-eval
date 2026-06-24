from langchain.chains import LLMChain
from langchain.chains.base import Chain
from langchain.llms import BaseLLM
from langchain.prompts import PromptTemplate

from prompts import QuestionGeneratorPromptTemplate


class QuestionGenerator(LLMChain):
    """Chain to generate questions based on the products available"""

    @classmethod
    def from_llm(cls, llm: BaseLLM, prompt_key: str, verbose: bool = True) -> LLMChain:
        """Get the response parser."""
        # Validate prompt_key against an allowlist to prevent prompt injection
        allowed_prompt_keys = ["question_generator_prompt", "another_valid_key"] # Define your allowed keys
        if prompt_key not in allowed_prompt_keys:
            raise ValueError(f"Invalid prompt_key: {prompt_key}. Must be one of {allowed_prompt_keys}")

        prompt = PromptTemplate(
            template=QuestionGeneratorPromptTemplate.get(prompt_key),
            input_variables=["products", "number_of_questions"],
        )
        return cls(prompt=prompt, llm=llm, verbose=verbose)


class NERGenerator(LLMChain):
    """Chain to generate questions based on the products available"""

    @classmethod
    def from_llm(cls, llm: BaseLLM, prompt_key: str, verbose: bool = True) -> LLMChain:
        """Get the response parser."""
        # Validate prompt_key against an allowlist to prevent prompt injection
        allowed_prompt_keys = ["ner_generator_prompt", "another_valid_ner_key"] # Define your allowed keys
        if prompt_key not in allowed_prompt_keys:
            raise ValueError(f"Invalid prompt_key: {prompt_key}. Must be one of {allowed_prompt_keys}")

        prompt = PromptTemplate(
            template=QuestionGeneratorPromptTemplate.get(prompt_key),
            input_variables=["sentences", "entity_name"],
        )
        return cls(prompt=prompt, llm=llm, verbose=verbose)
