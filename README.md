## Question-Answer Generator for Blogs, API/SDK Docs, Readme, Product Catalogs and more for LLM Applications

[![Python Version](https://img.shields.io/badge/python-3.9-blue.svg)](https://python.org)

[![codecov](https://codecov.io/gh/yourusername/question-answer-generator/branch/main/graph/badge.svg?token=yourcodecovtoken)](https://codecov.io/gh/yourusername/question-answer-generator)

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)

This project is a tool for generating question-answer pairs based on provided data. It allows you to generate questions related to product information by specifying various parameters such as the data file path, the number of questions to generate, and more.


| Trying to evaluate an LLM on massive documents without automated eval dataset. | Realizing the importance of eval dataset generation for accurate llm app evaluations. |
| ----------------------------------------------------------------------- | ------------------------------------------------------------------ |
| ![Confused Person](data/images/confused_person.png)                    | ![Confident Person](data/images/confident_person.png)             |

## Why Dataset Generation Matters

Evaluating LLM applications on massive documents can be a daunting task, especially when you don't have the right evaluation dataset. The quality and relevance of your dataset can significantly impact the accuracy of your LLM app evaluations for production deploy. Manual dataset creation & versioning can be time-consuming and error-prone, leading to inaccurate results.

## Prerequisites
- Python (>=3.9)
- Poetry (for dependency management)
- Docker (>=4.25.0)

## API EndPoints
These endpoints allow you to handle generation, fetch, evaluation, ranking & reporting

#### POST
```bash
* /generate/
* /evaluate/{id}
```

#### GET
```bash
* /download/{id}/
* /report/{id}/
```


## Installation & Usage

### 1. Clone this repository to your local machine:

   ```bash
   git clone https://github.com/sundi133/llm-datacraft.git
   cd question-answer-generator
   ```

### 2. Install the required dependencies using Poetry:

   ```bash
   poetry install
   ```
 
### 3. Start service
    ```bash 
    docker compose up --build
    ```

### 4. Generate Dataset for LLM + RAG Evaluation

### Parameters

|      Name           |   Required   |  Type   | Description                                                                                                              |
| ------------------- |:------------:|:-------:| ------------------------------------------------------------ |
| `file`              |   required   |  file   | The input data file (e.g., CSV, TXT, PDF, or HTML Page Link). |
| `description`       |   required   | string  | A description for the file to be ingested.                  |

### Request Example

```bash
curl -X POST http://localhost:8000/generate/ \
  -F "file=@example.txt" \
  -F "number_of_questions=3" \
  -F "name=3"
```
### Command Options Available

- `--data_path`: The path to the input data file (e.g., CSV, TXT, PDF or HTML Links).
- `--number_of_questions`: The number of questions to generate.
- `--sample_size`: The sample size for selecting groups.
- `--products_group_size`: The minimum number of products per group.
- `--group_columns`: Columns to group by (e.g., "brand,sub_category,category,gender").
- `--output_file`: The path to the output JSON file where question-answer pairs will be saved.
- `--prompt_key`: The prompt key to be used 
- `--llm_type`: The class to use from llmchain extension 
- `--metadata`: The path to any metadata file

### Response Example

```
{
    "message": "Generator in progress, Use the /download-qa-pairs/ endpoint to check the status of the generator",
    "gen_id": "f8e3670f5ff9440a84f93b00197ad697"
}
```

### 5. Download Dataset

### Parameters

|      Name  |   Required   |   Type   | Description                            |
| ----------- |:------------:|:--------:| -------------------------------------- |
| `gen_id`    |   required   |  string  | The unique ID of the generated dataset. |

### Request Example

```bash
curl -OJ http://localhost:8000/download/f8e3670f5ff9440a84f93b00197ad697
```

### 6. Run LLM + RAG Evaluator

### Parameters

|           Name  |   Required   |  Type   | Description                                |
| --------------- |:------------:|:-------:| ------------------------------------------ |
| `gen_id`        |   required   | string  | The unique ID of the generated dataset.     |
| `llm_endpoint`  |   required   | string  | The endpoint for the LLM (Language Model). |
| `wandb_log`     |   optional   | boolean | Whether to log using WandB.                 |

### Request Example

```bash
curl -X GET http://localhost:8000/evaluate/ \
-F "gen_id=f8e3670f5ff9440a84f93b00197ad697" \
-F "llm_endpoint=http://localhost:8001/chat/" \
-F "wandb_log=True"
```

### Response Example

```
{
    "message": "Ranker is complete, Use the /report/gen_id endpoint to download ranked reports for each question",
    "gen_id": "f8e3670f5ff9440a84f93b00197ad697"
}
```

### 7. Download LLM + RAG Evaluator Report

### Parameters

|      Name  |   Required   |   Type   | Description                        |
| ----------- |:------------:|:--------:| ---------------------------------- |
| `gen_id`    |   required   |  string  | The unique ID of the generated report. |

### Request Example

```bash
curl -OJ http://localhost:8000/report/f8e3670f5ff9440a84f93b00197ad697
```


## Example QA Datasets that are generated

In the provided command, we are generating 2 questions based on the `amazon_uk_shoes_cleaned.csv` data file. We are using a sample size of 3 and require a minimum of 3 products per group to generate questions. The questions will be grouped by the columns "brand," "sub_category," "category," and "gender," and the results will be saved to `qa_sample.json` in the `output` directory.

**Example pair of QA dataset generated from the input file of type csv with a sample product catalog**

```
{
"question": "What are the different categories of men's shoes available?", 
"answer": "The available categories of men's shoes are loafers & moccasins."
}

{
"question": "Are there any promotions available for the men's shoes?", 
"answer": "Yes, there is a promotion of up to 35% off on selected men's shoes."
}

{
"question": "What is the price range for Laredo Men's Lawton Western Boot?", 
"answer": - "The price range for Laredo Men's Lawton Western Boot is \u00a3117.19 - \u00a3143.41."
}

{
"question": "What is the material used for the outer sole of Laredo Men's Wanderer Boot?",
"answer": "The outer sole of Laredo Men's Wanderer Boot is made of manmade material."
}

{
"question": "What promotions are currently available for the Saucony Women Sports Shoes Jazz Original Vintage Blue?",
"answer": "The Saucony Women Sports Shoes Jazz Original Vintage Blue is currently on sale with a 25% discount."
}

{
"question": "What are the features of the Saucony Women's Jazz Original Trainers?",
"answer": "The Saucony Women's Jazz Original Trainers have a leather outer material, rubber sole, lace-up closure, and a flat heel type."
}
```

**Example pair of QA dataset generated from the input of type readme online docs along with links**

```
{
"question":"What are some examples of exceptions thrown by Javelin Python SDK?",
"answer":"Javelin Python SDK throws various exceptions for different error scenarios. For example, you can catch specific exceptions to handle errors related to authentication, network connectivity, or data validation.",
"url":"https://docs.getjavelin.io/docs/javelin-python/quickstart"
}

{
"question":"How can I access the data model in Javelin?",
"answer":"To access the data model in Javelin, you can refer to the documentation provided at the given URL.",
"url":"https://docs.getjavelin.io/docs/javelin-python/models#routes"
}

{
"question":"What are the fields available in the Javelin data model?",
"answer":"The Javelin data model includes various fields that can be used to store and manipulate data.",
"url":"https://docs.getjavelin.io/docs/javelin-python/models#model"
}

{
"question":"How does Javelin handle load balancing?",
"answer":"The documentation does not provide specific information on how Javelin handles load balancing.",
"url":"https://docs.getjavelin.io/docs/javelin-core/loadbalancing#__docusaurus_skipToContent_fallback"
}

{
"question":"What can Javelin do?",
"answer":"Javelin can send requests to models and retrieve responses based on the configured policies and route configurations.",
"url":"https://docs.getjavelin.io/docs/javelin-core/integration#llm-response"
}


```

## Linter
```bash
   poetry run flake8 src
   poetry run black src
```

## License

This project is licensed under the Apache 2.0 License - see the [LICENSE](LICENSE) file for details.

---