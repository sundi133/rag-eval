import nltk
import argparse
import asyncio
import wandb
import logging
import json
import os

from nltk.translate.bleu_score import sentence_bleu
from nltk.translate.bleu_score import SmoothingFunction
from nltk.translate.meteor_score import single_meteor_score
from rouge_score import rouge_scorer

from typing import List
from .utils import read_endpoint_configurations, read_qa_data, get_llm_answer

# Make sure NLTK data is downloaded (required for METEOR and ROUGE)
nltk.download("wordnet")
nltk.download("punkt")

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
ch = logging.StreamHandler()
ch.setFormatter(formatter)
logger.addHandler(ch)


async def evaluate_qa_data(
    qa_data_path: str,
    endpoint_configs: dict(),
    wandb_log: bool = False,
    output_file: str = "ranking.json",
) -> None:
    """
    Evaluate the quality of answers generated by different endpoints for a given set of questions.

    Args:
        qa_data_path (str): The path to the JSON file containing the QA data.
        qa_endpoints (str): The path to the JSON file containing the endpoint configurations.
        wandb_log (bool): Whether to log the results to Weights & Biases.

    Returns:
        None
    """

    # Read the qa dataset
    qa_data = read_qa_data(qa_data_path)

    for endpoint_config in endpoint_configs:
        logger.info(f"Endpoint Name: {endpoint_config['name']}")
        logger.info(f"Endpoint URL: {endpoint_config['url']}")
    for entry in qa_data:
        question = entry.get("question", "")
        answer = entry.get("answer", "")
        logger.info(f"Question: {question}")
        logger.info(f"Answer: {answer}")

    question_ranking = []
    scorer = rouge_scorer.RougeScorer(["rouge1", "rougeL"], use_stemmer=True)

    for entry in qa_data:
        question = entry.get("question", "")
        reference_answer = entry.get("answer", "")
        logger.info(f"Question: {question}")
        logger.info(f"Answer: {reference_answer}")
        for endpoint_config in endpoint_configs:
            logger.info(f"Endpoint Name: {endpoint_config['name']}")
            logger.info(f"Endpoint URL: {endpoint_config['url']}")
            logger.info(f"Question: {question}")
            candidate = await get_llm_answer(question, endpoint_config)
            logger.info(f"Answer: {candidate}")
            # Tokenize the sentences into lists of words
            reference_answer_tokens = nltk.word_tokenize(reference_answer.lower())
            candidate_tokens = nltk.word_tokenize(candidate.lower())

            # Calculate BLEU score
            bleu_score_val = sentence_bleu(
                [reference_answer_tokens],
                candidate_tokens,
                smoothing_function=SmoothingFunction().method4,
            )

            # Calculate ROUGE-L score
            rouge_l_score_val = scorer.score(reference_answer, candidate)[
                "rougeL"
            ].fmeasure

            # Calculate METEOR score
            meteor_score_val = single_meteor_score(
                reference_answer.split(" "), candidate.split(" ")
            )

            logger.info(f"BLEU score: {bleu_score_val}")
            logger.info(f"ROUGE-L score: {rouge_l_score_val}")
            logger.info(f"METEOR score: {meteor_score_val}")

            question_ranking.append(
                {
                    "endpoint_name": endpoint_config["name"],
                    "url": endpoint_config["url"],
                    "question": question,
                    "expected_response": reference_answer,
                    "endpoint_response": candidate,
                    "rouge_l_score": rouge_l_score_val,
                    "bleu_score": bleu_score_val,
                    "meteor_score": meteor_score_val,
                }
            )

        # Sort the endpoints based on their scores (highest to lowest)
        question_ranking = sorted(
            question_ranking,
            key=lambda x: (-x["rouge_l_score"], -x["bleu_score"], -x["meteor_score"]),
        )

    question_ranking = sorted(
        question_ranking,
        key=lambda x: (-x["rouge_l_score"], -x["bleu_score"], -x["meteor_score"]),
    )

    for ranking in question_ranking:
        logger.info(f"Question: {ranking['question']}")
        # log in wandb
        if wandb_log:
            wandb.log(
                {
                    "question": ranking["question"],
                    "expected_response": ranking["expected_response"],
                    "endpoint_response": ranking["endpoint_response"],
                    "endpoint_name": ranking["endpoint_name"],
                    "url": ranking["url"],
                    "rouge_l_score": ranking["rouge_l_score"],
                    "bleu_score": ranking["bleu_score"],
                    "meteor_score": ranking["meteor_score"],
                }
            )
        logger.info(
            {
                "question": ranking["question"],
                "expected_response": ranking["expected_response"],
                "endpoint_response": ranking["endpoint_response"],
                "endpoint_name": ranking["endpoint_name"],
                "url": ranking["url"],
                "rouge_l_score": ranking["rouge_l_score"],
                "bleu_score": ranking["bleu_score"],
                "meteor_score": ranking["meteor_score"],
            }
        )

    # rm file if exists
    if os.path.exists(output_file):
        os.remove(output_file)

    with open(output_file, "w") as op:
        json.dump(question_ranking, op, indent=4)

    if os.path.exists(output_file):
        logger.info(f"Ranking is completed and saved to {output_file}")

    logger.info("Ranking is completed")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Ranking the endpoints for each question"
    )

    parser.add_argument("--qa_data_path", type=str, help="Path to the input data file")

    parser.add_argument("--qa_endpoints", type=str, help="LLM Endpoints")

    parser.add_argument(
        "--wandb_log", type=bool, default=False, help="wandb logging enabled"
    )

    args = parser.parse_args()

    # Read and process endpoint configurations
    endpoint_configs = read_endpoint_configurations(args.qa_endpoints)

    asyncio.run(
        evaluate_qa_data(
            qa_data_path=args.qa_data_path,
            qa_endpoints=endpoint_configs,
            wandb_log=args.wandb_log,
        )
    )
