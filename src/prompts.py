QuestionGeneratorPromptTemplate = {
    "prompt_key_csv": """
    
        Follow the instructions below:
        Generate {number_of_questions} general chat questions and answer pairs for a customer who is inquiring about products without knowing about these products in advance. The customer will ask about products available, promotions available, about categories of products etc based on the products available in the below list:
        ===
        {products}
        ===

        Instructions:
        1. make sure the questions are relevant to the products available
        2. make sure the questions asked vary from each other
        3. make sure the questions are not repeated
        4. make sure the questions are not too long
        5. make sure the answers are relevant to the questions
        6. Do not generate fake questions and answers

        [ Generate each question and the relevant answer based on the products available in json format with following format:
            [
                {{
                    "question": "question 1",
                    "answer": "answer 1"
                }},
                {{
                    "question": "question 2",
                    "answer": "answer 2"
                }},
                ...
            ]
        ]

    """,
    "prompt_key_ner": """
        You are a dataset generator that is used to train a named entity recognition model
        There are a few sentences for which you have to generate training data in a specific JSON format like below:

        [
            {{
                "text": "Who is Nishanth?",
                "entities": [
                    {{
                        "start": 7,
                        "end": 15,
                        "label": "PERSON"
                    }}
                ]
            }},
            {{
                "text": "Who is Kamal Khumar?",
                "entities": [
                    {{
                        "start": 7,
                        "end": 19,
                        "label": "PERSON"
                    }}
                ]
            }},
            {{
                "text": "I like London and Berlin.",
                "entities": [
                    {{
                        "start": 7,
                        "end": 13,
                        "label": "LOC"
                    }},
                    {{
                        "start": 18,
                        "end": 24,
                        "label": "LOC"
                    }}
                ]
            }}
        ]


        Do the work for all the following sentences with the entity name {entity_name}

        ===
        {sentences}
        ===

        Instructions:
        1. make sure the sentences are relevant to the entity name
        2. make sure the sentences are not repeated
        3. make sure the sentences the output is in the above format of json

        [ Output format must be stringified json as mentioned above ]

    """,
    "prompt_key_readme": """
    
        Follow the instructions below:
        Generate {number_of_questions} general chat questions and answer pairs for a customer who is inquiring about readme documentation. The customer will ask about how the software will work, how to use the software, how to install the software etc based on the documentation provided below
        :
        ===
        {products}
        ===

        Instructions:
        1. make sure the questions are relevant to the software capabilities available in the documentation
        2. make sure the questions asked vary from each other
        3. make sure the questions are not repeated
        4. make sure the questions are not too long
        5. make sure the answers are relevant to the questions
        6. Do not generate fake questions and answers

        [ Generate each question and the relevant answer based on the documentation available in json format with following format:
            [
                {{
                    "question": "question 1",
                    "answer": "answer 1"
                }},
                {{
                    "question": "question 2",
                    "answer": "answer 2"
                }},
                ...
            ]
        ]

    """,
    "prompt_key_blogpost": """
    
        Follow the instructions below:
        Generate {number_of_questions} general chat questions and answer pairs for a customer who is inquiring about your blog posts. The customer will ask questions about the blog posts available in the below list:
        ===
        {products}
        ===

        Instructions:
        1. make sure the questions are relevant to the blog posts content
        2. make sure the questions asked vary from each other
        3. make sure the questions are not repeated
        4. make sure the questions are not too long
        5. make sure the answers are relevant to the questions
        6. Do not generate fake questions and answers

        [ Generate each question and the relevant answer based on the documentation available in json format with following format:
            [
                {{
                    "question": "question 1",
                    "answer": "answer 1"
                }},
                {{
                    "question": "question 2",
                    "answer": "answer 2"
                }},
                ...
            ]
        ]

    """,
}
