from nltk.translate.bleu_score import sentence_bleu
from nltk.translate.bleu_score import SmoothingFunction
from nltk.translate.bleu_score import corpus_bleu
from nltk.translate.bleu_score import sentence_bleu
from nltk.translate.bleu_score import sentence_bleu
from nltk.translate.meteor_score import meteor_score
from nltk.translate.rouge_score import rouge_n, rouge_l, rouge_w
import nltk
import random
import json

# Make sure NLTK data is downloaded (required for METEOR and ROUGE)
nltk.download("wordnet")
nltk.download("punkt")


# Read the JSON file and load its content
def read_qa_data(qa_data_path):
    try:
        with open(qa_data_path, "r") as json_file:
            qa_data = json.load(json_file)
            return qa_data
    except FileNotFoundError:
        print(f"The file '{json_file_path}' was not found.")
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")


# Function to read and process endpoint configurations
def read_endpoint_configurations(file_path):
    try:
        with open(file_path, "r") as json_file:
            endpoint_configs = json.load(json_file)
            return endpoint_configs
    except FileNotFoundError:
        print(f"The file '{file_path}' was not found.")
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")


def score_answer(question, answer, endpoint_answer):
    pass


def get_llm_answer(question, endpoint_config):
    pass


def evaluate_qa_data(**args):
    qa_data_path = args.qa_data_path
    # Specify the path to your JSON configuration file
    qa_endpoints = args.qa_endpoints

    # Read and process endpoint configurations
    endpoint_configs = read_endpoint_configurations(qa_endpoints)

    # Read the qa dataset
    qa_data = read_qa_data(qa_data_path)

    for endpoint_config in endpoint_configs:
        print(f"Endpoint Name: {endpoint_config['name']}")
        print(f"Endpoint URL: {endpoint_config['url']}")
        print()
    for entry in qa_data:
        question = entry.get("question", "")
        answer = entry.get("answer", "")
        print(f"Question: {question}")
        print(f"Answer: {answer}")

    question_ranking = []

    for entry in qa_data:
        question = entry.get("question", "")
        reference_answer = entry.get("answer", "")
        print(f"Question: {question}")
        print(f"Answer: {reference_answer}")
        print()
        for endpoint_config in endpoint_configs:
            print(f"Endpoint Name: {endpoint_config['name']}")
            print(f"Endpoint URL: {endpoint_config['url']}")
            candidate = get_llm_answer(question, endpoint_config)
            print(f"Answer: {candidate}")
            # Tokenize the sentences into lists of words
            reference_answer_tokens = nltk.word_tokenize(reference_answer.lower())
            candidate_tokens = nltk.word_tokenize(candidate.lower())

            # Calculate BLEU score
            bleu_score = sentence_bleu(
                [reference_answer_tokens],
                candidate_tokens,
                smoothing_function=SmoothingFunction().method4,
            )

            # Calculate ROUGE-L score
            rouge_l_score = rouge_l([reference_answer], [candidate])

            # Calculate METEOR score
            meteor_score = meteor_score([reference_answer], candidate)

            question_ranking.append(
                {
                    "endpoint_name": endpoint_config["name"],
                    "url": endpoint_config["url"],
                    "question": question,
                    "answer": reference_answer,
                    "rouge_l_score": rouge_l_score,
                    "bleu_score": bleu_score,
                    "meteor_score": meteor_score,
                }
            )

        # Sort the endpoints based on their scores (highest to lowest)
        question_ranking = sorted(
            question_ranking,
            key=lambda x: (-x["rouge_l_score"], -x["bleu_score"], -x["meteor_score"]),
        )
        ranked_endpoints.append({"question": question, "ranking": question_ranking})

    # Print the ranked endpoints for each question
    for ranking in ranked_endpoints:
        print(f"Question: {ranking['question']}")
        for i, endpoint in enumerate(ranking["ranking"]):
            # log in wandb
            if args.wandb:
                wandb.log(
                    {
                        "question": ranking["question"],
                        "endpoint_name": endpoint["endpoint_name"],
                        "url": endpoint["url"],
                        "rouge_l_score": endpoint["rouge_l_score"],
                        "bleu_score": endpoint["bleu_score"],
                        "meteor_score": endpoint["meteor_score"],
                    }
                )
            print(
                {
                    "question": ranking["question"],
                    "endpoint_name": endpoint["endpoint_name"],
                    "url": endpoint["url"],
                    "rouge_l_score": endpoint["rouge_l_score"],
                    "bleu_score": endpoint["bleu_score"],
                    "meteor_score": endpoint["meteor_score"],
                }
            )

        print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Ranking the endpoints for each question"
    )

    parser.add_argument("--qa_data_path", type=str, help="Path to the input data file")
    parser.add_argument("--qa_endpoints", type=str, help="LLM Endpoints")
    parser.add_argument("--wandb", type=bool, default=False, help="wandb logging")

    args = parser.parse_args()
    evaluate_qa_data(**vars(args))
