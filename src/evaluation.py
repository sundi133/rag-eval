import logging
import argparse
import asyncio
import json
import os
import requests
import random
import uuid
import time
import json
import requests
import aiohttp

from typing import Dict, Any, Optional
from sqlalchemy import select, create_engine, desc
from langchain.chat_models import ChatOpenAI
from typing import List
from sqlalchemy.orm import Session
from datetime import datetime
from fastapi_sqlalchemy import DBSessionMiddleware, db
from rouge_score import rouge_scorer

from .utils import (
    select_processor,
    select_llm,
    save_simulation_results,
    generate_random_hex_user_id,
    update_simulation_status,
)
from .models import (
    Dataset,
    LLMEndpoint,
    QAData,
    Assessments,
    EvaluationProfiles,
    EvaluationRuns,
)
from .llms import Datagen, DatagenNER, DatagenMultiChunkQA, DataEval
from .prompts import QuestionGeneratorPromptTemplate

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
ch = logging.StreamHandler()
ch.setFormatter(formatter)
logger.addHandler(ch)
logger = logging.getLogger(__name__)


def evaluation_task(
    dataset_id: int,
    evaluation_id: int,
    chat_id: int,
    org_id: str,
    user_id: str,
    question: str,
    verified_answer: str,
    verified_reference_context: str,
    app_generated_answer: str,
    app_generated_context: str,
    model_name: str,
    evaluation_user_prompt: str,
    simulation_id: int,
    simulation_run_id: int,
    openai_api_key: Optional[str] = None,
    verbose: Optional[bool] = False,
) -> None:
    """
    This is the main function that handles the evaluation task.
    """
    try:
        if evaluation_user_prompt == "":
            evaluation_user_prompt = QuestionGeneratorPromptTemplate.get(
                "evaluation_prompt"
            )

        
        llm_openai_gpt = ChatOpenAI(
            temperature=0.1,
            model=model_name,
            request_timeout=120,
            max_tokens=120,
            openai_api_key=openai_api_key
            if openai_api_key
            else os.environ.get("OPENAI_API_KEY"),
        )

        data_eval = DataEval.from_llm(
            llm_openai_gpt, evaluation_user_prompt, verbose=verbose
        )

        evaluation_response = data_eval.run(
            question=question,
            verified_answer=verified_answer,
            app_generated_answer=app_generated_answer,
        )

        evaluation = json.loads(evaluation_response)

        
        score = evaluation["score"]
        score_reason = evaluation["reason"]
        userid = generate_random_hex_user_id()

        save_simulation_results(
            simulation_id,
            simulation_run_id,
            userid,
            org_id,
            None,
            dataset_id,
            chat_id,
            app_generated_answer,
            score,
            score_reason,
            evaluation_id,
        )

        logger.info(
            {
                "message": "Finished simulation",
                "simulation_id": simulation_id,
                "simulation_run_id": simulation_run_id,
                "org_id": org_id,
                "dataset_id": dataset_id,
                "chat_id": chat_id,
                "evaluation_id": evaluation_id,
            }
        )
    except Exception as e:
        logger.error(
            {
                "message": "Error running simulation",
                "simulation_id": simulation_id,
                "simulation_run_id": simulation_run_id,
                "org_id": org_id,
                "dataset_id": dataset_id,
                "chat_id": chat_id,
                "evaluation_id": evaluation_id,
                "error": str(e),
            }
        )
