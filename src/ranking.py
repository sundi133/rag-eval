if __name__ == "__main__":
    import random
    import json

    parser = argparse.ArgumentParser(
        description="Ranking the endpoints for each question"
    )

    parser.add_argument("--qa_data_path", type=str, help="Path to the input data file")
    parser.add_argument("--qa_endpoints", type=str, help="LLM Endpoints")

    args = parser.parse_args()

    qa_data_path = args.qa_data_path
    # Specify the path to your JSON configuration file
    qa_endpoints = args.qa_endpoints

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

    # Read and process endpoint configurations
    endpoint_configs = read_endpoint_configurations(qa_endpoints)
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

    # Function to calculate a simple score for each endpoint's answer
    def score_answer(question, answer):
        # In this example, we use a random score (0 to 1) for illustration
        return random.uniform(0, 1)

    question_ranking = []

    for entry in qa_data:
        question = entry.get("question", "")
        answer = entry.get("answer", "")
        print(f"Question: {question}")
        print(f"Answer: {answer}")
        print()
        for endpoint_config in endpoint_configs:
            print(f"Endpoint Name: {endpoint_config['name']}")
            print(f"Endpoint URL: {endpoint_config['url']}")
            endpoint_score = score_answer(question, endpoint["answer"])
            question_ranking.append(
                {
                    "endpoint": endpoint_config["name"],
                    "score": endpoint_score,
                    "url": endpoint_config["url"],
                    "question": question,
                    "answer": endpoint["answer"],
                }
            )

        # Sort the endpoints based on their scores (highest to lowest)
        question_ranking = sorted(
            question_ranking, key=lambda x: x["score"], reverse=True
        )
        ranked_endpoints.append({"question": question, "ranking": question_ranking})

    # Print the ranked endpoints for each question
    for ranking in ranked_endpoints:
        print(f"Question: {ranking['question']}")
        for i, endpoint in enumerate(ranking["ranking"], start=1):
            print(f"{i}. {endpoint['endpoint']} - Score: {endpoint['score']:.2f}")
            # log in wandb
            wandb.log({"question": ranking["question"]})
            wandb.log({"endpoint": endpoint["endpoint"]})
            wandb.log({"score": endpoint["score"]})
        print()
