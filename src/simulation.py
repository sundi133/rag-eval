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
from typing import Dict, Any, Optional

from sqlalchemy import select, create_engine, desc
from langchain.chat_models import ChatOpenAI
from typing import List
from .utils import select_processor, select_llm
from .models import Dataset, LLMEndpoint, QAData, Evaluation, SimulationProfile, SimulationRuns
from sqlalchemy.orm import Session
from datetime import datetime
from fastapi_sqlalchemy import DBSessionMiddleware, db
from rouge_score import rouge_scorer
import aiohttp


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
ch = logging.StreamHandler()
ch.setFormatter(formatter)
logger.addHandler(ch)


logger = logging.getLogger(__name__)


async def get_llm_answer(
    endpoint_url: str, payload_data: json, payload_format: str, timeout: int = 15
) -> json:
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(
                endpoint_url, data=payload_data, timeout=timeout
            ) as response:
                if response.status == 200:
                    if payload_format == "json":
                        return await response.json()
                    else:
                        return {"data": await response.text()}
                else:
                    logger.error(f"Request failed with status code {response.status}.")
                    return {"data": ""}
        except Exception as e:
            logger.error(f"Error getting answer from endpoint: {str(e)}")
            return {"data": ""}


def generate_random_hex_user_id() -> str:
    """
    Generate a random user ID.
    """
    return f"user_id_{uuid.uuid4().hex.upper()[0:12]}"


def score_answer(question: str, answer: str, endpoint_answer: str) -> float:
    scorer = rouge_scorer.RougeScorer(["rouge1", "rougeL"], use_stemmer=True)
    rouge_l_score_val = scorer.score(answer, endpoint_answer)["rougeL"].fmeasure
    return rouge_l_score_val


def save_simulation_results(
    simulation_id: int,
    simulation_run_id: int,
    user_id: str,
    org_id: int,
    endpoint_url_id: int,
    dataset_id: int,
    qa_data_id: int,
    response: str,
    score: float,
    evaluation_id: str = None,
) -> None:
    """
    Save the results of a simulation.
    """
    evaluation = Evaluation(
        simulation_id=simulation_id,
        simulation_run_id=simulation_run_id,
        simulation_userid=user_id,
        orgid=org_id,
        llm_endpoint_id=endpoint_url_id,
        dataset_id=dataset_id,
        qa_data_id=qa_data_id,
        endpoint_response=response,
        score=score,
        evaluation_id=evaluation_id,
    )
    db.session.add(evaluation)
    db.session.commit()


def update_simulation_status(simulation_id, simulation_run_id, org_id, status):
    try:
        # Start a transaction
        db.session.begin()

        # Query and update SimulationProfile
        simulation_profile = db.session.query(SimulationProfile).filter(
            SimulationProfile.id == int(simulation_id),
            SimulationProfile.orgid == org_id
        ).first()

        if simulation_profile:
            simulation_profile.status = status
        else:
            raise ValueError("SimulationProfile not found")

        # Query and update SimulationRuns
        simulation_run = db.session.query(SimulationRuns).filter(
            SimulationRuns.id == simulation_run_id,
            SimulationRuns.orgid == org_id
        ).first()

        if simulation_run:
            simulation_run.run_status = status
        else:
            raise ValueError("SimulationRuns not found")

        # Commit the transaction
        db.session.commit()
    except Exception as e:
        # Rollback the transaction in case of error
        db.session.rollback()
        raise e

def simulation_task(
    simulation_id: int,
    simulation_run_id: int,
    user_id: int,
    org_id: int,
    endpoint_url_id: int,
    dataset_id: int,
    num_users: int,
    percentage_of_questions: int,
    order_of_questions: str,
) -> None:
    # Get the endpoint URL
    try:
        query = db.session.query(LLMEndpoint).filter(
            LLMEndpoint.id == endpoint_url_id, LLMEndpoint.orgid == org_id
        )
        endpoint = query.first()
        endpoint_url = endpoint.endpoint_url
        requests_per_minute = endpoint.requests_per_minute
        delay_seconds = 60 / requests_per_minute
        delay_milliseconds = delay_seconds * 1000
        payload_user_key = endpoint.payload_user_key
        payload_message_key = endpoint.payload_message_key
        payload_response_key = endpoint.payload_response_key
        payload_format = endpoint.payload_format if endpoint.payload_format else "text"
        payload_format = payload_format.lower()
        
        evaluation_id = f"{uuid.uuid4().hex.upper()[0:32]}"
        # Get the evaluation based on the simulation_id
        evaluation_query = db.session.query(Evaluation).filter(
            Evaluation.simulation_id == simulation_id,
            Evaluation.orgid == org_id,
        )
        evaluation = evaluation_query.first()
        if evaluation:
            evaluation_id = evaluation.evaluation_id


        # use percentage_of_questions to determine the number of questions to ask and limit the number of questions to ask
        qadata_query = (
            db.session.query(QAData)
            .filter(QAData.orgid == org_id, QAData.dataset_id == dataset_id)
            .order_by(desc(QAData.ts))
        )

        qa_data = qadata_query.all()

        simulation_query = db.session.query(SimulationProfile).filter(
            SimulationProfile.id == simulation_id, SimulationProfile.orgid == org_id
        )
        simulation = simulation_query.first()
        num_users = simulation.num_users
        # create a list of user id generate_random_hex_user_id for each user
        user_ids = [generate_random_hex_user_id() for _ in range(num_users)]

        # Get the evaluation
        for data in qa_data:
            qa_data_id = data.id
            # choose a random user id from the list of user ids
            userid = random.choice(user_ids)
            chat_messages = data.chat_messages

            json_chat_messages = json.loads(chat_messages)["question_answer"]
            question = json_chat_messages["question"]
            answer = json_chat_messages["answer"]

            # Access follow-up questions and answers
            follow_up_data = {}
            for key, value in json_chat_messages.items():
                if key.startswith("follow-up_question"):
                    index = key.split()[-1]
                    follow_up_data[index] = {"Question": value}
                elif key.startswith("follow-up_answer"):
                    index = key.split()[-1]
                    follow_up_data[index]["Answer"] = value

            payload_data = {payload_user_key: userid, payload_message_key: question}

            response = asyncio.run(
                get_llm_answer(
                    endpoint_url, payload_data=payload_data, payload_format=payload_format
                )
            )

            if payload_format == "json" and payload_response_key in response:
                response = response[payload_response_key]
            else:
                response = response["data"]

            score = score_answer(question, answer, response)
            logger.info(
                {
                    "message": "Generated data",
                    "data": json.dumps(payload_data),
                    "answer": answer,
                    "payload_format": payload_format,
                    "payload_response_key": payload_response_key,
                    "response": json.dumps(response),
                    "score": score,
                }
            )
            save_simulation_results(
                simulation_id,
                simulation_run_id,
                userid,
                org_id,
                endpoint_url_id,
                dataset_id,
                qa_data_id,
                response,
                score,
                evaluation_id,
            )

            for index, fuq_data in sorted(follow_up_data.items()):
                fuq = fuq_data["Question"]
                fua = fuq_data.get("Answer", "")
                payload_data = {payload_user_key: userid, payload_message_key: question}
                response = asyncio.run(
                    get_llm_answer(
                        endpoint_url,
                        payload_data=payload_data,
                        payload_format=payload_format,
                    )
                )
                if payload_format == "json" and payload_response_key in response:
                    response = response[payload_response_key]
                else:
                    response = response["data"]
                score = score_answer(fuq, fua, response)
                save_simulation_results(
                    simulation_id,
                    simulation_run_id,
                    userid,
                    org_id,
                    endpoint_url_id,
                    dataset_id,
                    qa_data_id,
                    response,
                    score,
                    evaluation_id,
                )
                time.sleep(delay_milliseconds)

        update_simulation_status(simulation_id, simulation_run_id, org_id, "completed")

        logger.info(
            {
                "message": "Finished simulation",
                "simulation_id": simulation_id,
                "simulation_run_id": simulation_run_id,
                "org_id": org_id,
                "endpoint_url_id": endpoint_url_id,
                "dataset_id": dataset_id,
                "num_users": num_users,
                "percentage_of_questions": percentage_of_questions,
                "order_of_questions": order_of_questions,
            }
        )
    except Exception as e:
        update_simulation_status(simulation_id, simulation_run_id, org_id, "error")

        logger.error(
            {
                "message": "Error running simulation",
                "simulation_id": simulation_id,
                "simulation_run_id": simulation_run_id,
                "org_id": org_id,
                "endpoint_url_id": endpoint_url_id,
                "dataset_id": dataset_id,
                "num_users": num_users,
                "percentage_of_questions": percentage_of_questions,
                "order_of_questions": order_of_questions,
                "error": str(e),
            }
        )


    return
