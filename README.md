## Datagen & RagEval for various LLM (Large Language Model) with the RAG (Retrieval-Augmented Generation) Apps on private data
- Blogs
- API & Docs
- Readme/PDF 
- Product Catalogs
- Any Unstructured Data Dources 

## Types of QA Dataset Generation

#### Simple QA Generation
This generates context-independent self-contained question-answer datasets.

#### Follow-up Continuous Questions Generator
This generator crafts AI-powered questions that build upon existing conversation content. By measuring the effectiveness of follow-ups, it unlocks deeper insights and drives natural dialogue flow.

#### Turn-Key New Questions 
Generate new questions that seamlessly shift the conversation to unexplored areas. This flexibility allows you to assess your app's ability to handle context changes and provide relevant information in diverse situations.

#### Questions Spread Across Multiple Chunks
This option creates thematically linked questions across large data chunks (>4k). By requiring holistic analysis of multiple segments, it pushes your AI's comprehension and reveals hidden connections within your content.


[![Python Version](https://img.shields.io/badge/python-3.9-blue.svg)](https://python.org)

[![codecov](https://codecov.io/gh/yourusername/question-answer-generator/branch/main/graph/badge.svg?token=yourcodecovtoken)](https://codecov.io/gh/yourusername/question-answer-generator)

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)

| Trying to evaluate an LLM on massive documents without automated eval dataset. | Realizing the importance of eval dataset generation for accurate llm app evaluations. |
| ----------------------------------------------------------------------- | ------------------------------------------------------------------ |
| ![Confused Person](data/images/confused_person.png)                    | ![Confident Person](data/images/confident_person.png)             |


## Prerequisites
- Python (>=3.9)
- Poetry (for dependency management)
- Docker (>=4.25.0)

## API EndPoints
These endpoints allow you to handle 
- generation
- download
- evaluation on your llm endpoint
- ranking & reporting

#### POST methods
```bash
* /generate/
* /evaluate/{id}
```

#### GET methods
```bash
* /download/{id}/
* /report/{id}/
```


## Usage

### 1. Clone this repository to your local machine:

   ```bash
   git clone https://github.com/sundi133/openeval.git
   cd openeval
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
-F "file=@data.csv" \
-F "number_of_questions=5" \
-F "sample_size=5" \
-F "prompt_key=prompt_key_csv" \
-F "llm_type=.csv"
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
curl -X POST http://localhost:8000/evaluate/ \
-F "gen_id=f8e3670f5ff9440a84f93b00197ad697" \
-F "llm_endpoint=http://llm-rag-app-1:8001/chat/" \
-F "wandb_log=True" \
-F "sampling_factor=0.2" 
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
curl -OJ  http://localhost:8000/ranking/ffc64a1150bb4d07ba2e355a32a3f398  
```


## Example datasets generated

In the provided command, we are generating 2 questions based on the `amazon_uk_shoes_cleaned.csv` data file. We are using a sample size of 3 and require a minimum of 3 products per group to generate questions. The questions will be grouped by the columns "brand," "sub_category," "category," and "gender," and the results will be saved to `qa_sample.json` in the `output` directory.

**Sample pair of QA dataset generated from the input file of type csv with a sample product catalog**

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

```

**Sample pair of QA dataset generated from the input of type readme online docs along with links**

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

```


## Examples of evaluation report
```bash
[  
    {
        "endpoint_name": "llm-fb7c6163791d24cb082c6407163185b04",
        "url": "http://llm-rag-app-1:8001/chat/",
        "question": "Where can I find the Wikipedia page about John Doe?",
        "expected_response": "You can find the Wikipedia page about John Doe by visiting the following link: https://en.wikipedia.org/wiki/John_Doe",
        "endpoint_response": "\"You can find the Wikipedia page about John Doe by searching for his name on the Wikipedia website.\"",
        "rouge_l_score": 0.6153846153846153,
        "bleu_score": 0.44323796909955787,
        "meteor_score": 0.6326797385620915
    },
    {
        "endpoint_name": "llm-fb7c6163791d24cb082c6407163185b04",
        "url": "http://llm-rag-app-1:8001/chat/",
        "question": "What kind of information can I expect to find on the Wikipedia page about John Doe?",
        "expected_response": "The Wikipedia page about John Doe contains details about his personal life, career, accomplishments, and any significant events or controversies related to him.",
        "endpoint_response": "\"On the Wikipedia page about John Doe, you can expect to find a variety of information about him. This may include his personal background, such as his birthdate, place of birth, and family information. It may also provide details about his education, career, and notable achievements. Additionally, the page may cover his involvement in any significant events or contributions to a particular field. Furthermore, you can expect to find information about his public image, including any controversies or criticisms associated with him. The page may also include references and external links for further reading and verification of the information provided.\"",
        "rouge_l_score": 0.2764227642276423,
        "bleu_score": 0.08875250765948056,
        "meteor_score": 0.3804238549081112
    },
    {
        "endpoint_name": "llm-fb7c6163791d24cb082c6407163185b04",
        "url": "http://llm-rag-app-1:8001/chat/",
        "question": "What is the purpose of the readme file?",
        "expected_response": "The readme file provides information about the content and instructions for using the test file.",
        "endpoint_response": "\"The purpose of the readme file is to provide important information and instructions about a particular project or software. It typically includes details about the project's purpose, installation instructions, usage guidelines, and any additional resources or dependencies required. The readme file serves as a helpful guide for users and developers to understand and navigate the project effectively.\"",
        "rouge_l_score": 0.273972602739726,
        "bleu_score": 0.032836768734999404,
        "meteor_score": 0.35769628099173556
    },
    {
        "endpoint_name": "llm-fb7c6163791d24cb082c6407163185b04",
        "url": "http://llm-rag-app-1:8001/chat/",
        "question": "What is the content of the Wikipedia page about John Doe?",
        "expected_response": "The Wikipedia page about John Doe provides information about his background, achievements, and notable contributions.",
        "endpoint_response": "\"I'm sorry, but as an AI assistant, I don't have the ability to retrieve specific information from the internet in real-time. However, you can easily find the content of the Wikipedia page about John Doe by searching for \\\"John Doe Wikipedia\\\" on any search engine. This will direct you to the actual Wikipedia page where you can read all the information about John Doe.\"",
        "rouge_l_score": 0.19512195121951217,
        "bleu_score": 0.07027194436347371,
        "meteor_score": 0.31721105527638194
    },
    {
        "endpoint_name": "llm-fb7c6163791d24cb082c6407163185b04",
        "url": "http://llm-rag-app-1:8001/chat/",
        "question": "Is there any specific format or structure for the test file?",
        "expected_response": "The readme file does not mention any specific format or structure for the test file.",
        "endpoint_response": "\"Yes, there is typically a specific format or structure for a test file. The format and structure may vary depending on the specific testing framework or tool being used. It is important to follow the guidelines provided by the testing framework or tool to ensure that the test file is correctly formatted and structured. This may include specifying the test cases, input data, expected results, and any necessary setup or teardown steps. It is recommended to refer to the documentation or guidelines of the testing framework or tool for more specific information on the required format and structure of the test file.\"",
        "rouge_l_score": 0.15384615384615385,
        "bleu_score": 0.053436696733189626,
        "meteor_score": 0.3113279418659166
    }
]
```

## Linter
```bash
   poetry run flake8 src
   poetry run black src
```

## License

This project is licensed under the Apache 2.0 License - see the [LICENSE](LICENSE) file for details.

---