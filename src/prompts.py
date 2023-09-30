QuestionGeneratorPromptTemplate = {
    "prompt_key_1": """
    
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
    "prompt_key_2": """
    
    """,
}
