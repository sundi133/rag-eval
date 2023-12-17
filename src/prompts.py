QuestionGeneratorPromptTemplate = {
    "prompt_key_csv": """
    
        Follow the instructions below:
        Generate {number_of_questions} general chat questions and answer pairs for a customer who is inquiring about products without knowing about these products in advance. 
        The schema of the csv file is as follows:
        ===
        {schema}
        ===

        The customer will ask about products available, promotions available, about categories of products etc based on the products available in the below list:
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
    "prompt_key_csv_stateful_contextual_multilevel": """
    
        Follow the instructions below:
        
        Instructions:
        Imagine you are a chat data simulator simulating customer chats based on a comprehensive set of products of any provided content. 
        Generate {number_of_questions} customer chat questions and answer pairs creating a thoughtful conversational flow that naturally progresses from one question to the next.
        Include at least 3 follow-up questions per initial question.
        Incorporate a series of follow-up questions that seamlessly build upon the previous answers provided and create a natural conversational flow using pronouns like it, its, this, that, these, those, them as applicable to foster continuity and depth in the conversation. 
        Ensure that each follow-up question leverages the information from the preceding answers to delve deeper into the topic and elicit nuanced insights 
        Ensuring all responses are factually accurate and based on the information in content provided. 
        Think step by step carefully and creatively about how to use the information provided to generate a natural conversation that flows well and is engaging for the customer.

        Here is an example of a chat messages with contextual answers and follow-up questions, use these as a reference to generate your own questions and answers for the content provided:
        ===
        Question 1: What exactly is the difference between finance and economics? I keep seeing them mentioned together, but I'm not sure how they're distinct.

        Answer: You're right, they are closely related fields, but there are some key differences. Finance focuses specifically on the management and flow of money, capital assets, and financial instruments. It's concerned with things like investments, loans, and banking activities. Economics, on the other hand, has a broader scope. It deals with the production, distribution, and consumption of goods and services in an entire economy. So, while finance looks at individual financial activities, economics takes a more holistic view of how these activities interact and influence the whole system.

        Follow-up question 1: That makes sense. So, is it fair to say that finance is like the engine that drives the economic machine?

        Follow-up answer 1: That's a great analogy! Finance plays a crucial role in providing the resources and mechanisms needed for economic activity to flourish. Without efficient financial systems, businesses wouldn't have access to capital for growth, individuals wouldn't be able to invest or manage their savings effectively, and governments wouldn't have the means to fund public projects.

        Follow-up question 2: Are there any specific areas of finance that are particularly important for the overall health of an economy?

        Follow-up answer 2: Absolutely! Financial stability, which involves managing risks and ensuring the smooth functioning of financial institutions, is critical for economic stability. Additionally, efficient capital markets, where investments are channeled towards productive activities, are essential for driving economic growth. And let's not forget the role of financial regulation in maintaining a fair and transparent financial system, which fosters trust and encourages economic activity.

        === end of example ===

        The provided content is as follows:
        ===
        {products}
        === end of content ===

        The schema of the csv file is as follows:
        ===
        {schema}
        === end of schema ===
        

        [ Generate each question and the relevant answer with contextual follow up questions, answers upto a depth of level 3 based on the documentation available in json format with following format:
            [
                {{
                    "question": "question 1",
                    "answer": "answer 1",
                    "follow_up_question_1": "follow up question contextually relevant to answer using pronouns like it, its, this, that, these, those, them as applicable",
                    "follow_up_answer_1": "follow up answer to follow up question 1",
                    "follow_up_question_2": "follow up question contextually relevant to follow_up_answer_1 using pronouns it, its, this, that, these, those, them as applicable",
                    "follow_up_answer_2": "follow up answer to follow up question 2",
                    ...
                    "follow_up_question": "follow up question contextually relevant to follow_up_answer_N-1",
                    "follow_up_answer": "follow up answer N"
                }},
                {{
                    "question": "question 2",
                    "answer": "answer 2",
                    "follow_up_question_1": "follow up question contextually relevant to answer using pronouns like it, its, this, that, these, those, them as applicable",
                    "follow_up_answer_1": "follow up answer to follow up question 1",
                    "follow_up_question_2": "follow up question contextually relevant to follow_up_answer_1 using pronouns like it, its, this, that, these, those, them as applicable",
                    "follow_up_answer_2": "follow up answer to follow up question 2",
                    ...
                    "follow_up_question": "follow up question contextually relevant to follow_up_answer_N-1",
                    "follow_up_answer": "follow up answer N"
                }},
                ...
            ]
        ]


    """,
    "prompt_key_ner_sentences": """
        Generate some sentences with the entity name {entity_name} in each sentence.
        The sentences must have '{entity_name}' in the sentences.
        The sentences should be real which are used in chat conversations like customer support or personal conversations. 
        Generate the {sample_size} sentences in the following JSON format:
        {{
            "sentences": [
                {{ "sentence" : "sentence 1"}},
                {{ "sentence" : "sentence 2"}},
                ...
            ]
        }}
    """,
    "prompt_key_ner": """
        You are a dataset generator that is used to train a named entity recognition model
        The start and end indices of the entities should be provided in the training data
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
        3, make sure the start and end indices are correct
        4. make sure the sentences the output is in the above format of json

        [ Output format must be stringified json as mentioned above ]

    """,
    "prompt_key_api_documentation": """
    
        Follow the instructions below:
        Generate {number_of_questions} general chat questions and answer pairs for a customer who is inquiring who is inquiring about the information provided in a API documentations. 
        The customer will ask about how the API's and integrations of the software sdk will work, how to use it for their own purposes,  the customer might make purchases decisions based on the quality of the information provided in the generated pairs. Generate high quality pairs based on information provided as follows:
        :
        ===
        {products}
        ===

        Instructions:
        1. make sure the questions are relevant to the content provided and available in the documentation provided
        2. make sure the questions asked vary from each other
        3. make sure the questions are not repeated and answers are detailed within 25 to 140 words
        4. make sure the questions are crisp and short and attention grabbing
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
    "prompt_key_api_documentation_stateful_contextual_multilevel": """
    
        Follow the instructions below:
        Generate {number_of_questions} general chat questions and answer pairs for a customer who is inquiring who is inquiring about the information provided in a API documentations. 
        The customer will ask about how the API's and integrations of the software sdk will work, how to use it for their own purposes,  the customer might make purchases decisions based on the quality of the information provided in the generated pairs. Generate high quality pairs based on information provided as follows:
        :
        ===
        {products}
        ===

        Instructions:
        1. make sure the questions are relevant to the content provided and available in the documentation provided
        2. make sure the questions asked vary from each other
        3. make sure the questions are not repeated and answers are detailed within 25 to 140 words
        4. make sure the questions are crisp and short and attention grabbing
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
        Generate {number_of_questions} general chat questions and answer pairs for a customer who is inquiring about the information provided in a blog post. The customer might make purchases decisions based on the quality of the information provided in the generated pairs. Generate the pairs based on information provided as follows:
        ===
        {products}
        ===

        Instructions:
        1. make sure the questions are relevant to the blog posts content provided and details provided in the blog post
        2. make sure the questions asked vary from each other
        3. make sure the questions are not repeated and answers are detailed within 25 to 140 words
        4. make sure the questions are crisp and short and attention grabbing
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
    "prompt_key_blogpost_stateful_contextual_multilevel": """
    
        Follow the instructions below:
        Generate {number_of_questions} general chat questions and answer pairs for a customer who is inquiring about the information provided in a blog post. The customer might make purchases decisions based on the quality of the information provided in the generated pairs. Generate the pairs based on information provided as follows:
        ===
        {products}
        ===

        Instructions:
        1. make sure the questions are relevant to the blog posts content provided and details provided in the blog post
        2. make sure the questions asked vary from each other
        3. make sure the questions are not repeated and answers are detailed within 25 to 140 words
        4. make sure the questions are crisp and short and attention grabbing
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
    "prompt_key_readme": """
    
        Follow the instructions below:
        Generate {number_of_questions} general chat questions and answer pairs for a customer who is inquiring about the information provided in a readme file. The customer might make ask any questions to make informed decision making based on the quality of the information provided in the readme file. Generate the pairs based on information provided as follows:
        ===
        {products}
        ===

        Instructions:
        1. make sure the generate questions are relevant to the content provided
        2. make sure the questions asked vary from each other
        3. make sure the questions are not repeated and answers are detailed within 25 to 140 words
        4. make sure the questions are crisp and short and attention grabbing
        5. make sure the answers are relevant to the questions
        6. Do not generate fake questions and answers
        7. If the content is less then 10 words, generate a empty list

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
    "prompt_key_readme_stateful_contextual_multilevel": """
    
        Instructions:
        Imagine you are a chat data simulator simulating customer chats based on a comprehensive document of any provided content. 
        Generate {number_of_questions} customer chat questions and answer pairs creating a thoughtful conversational flow that naturally progresses from one question to the next.
        Include at least 3 follow-up questions per initial question.
        Incorporate a series of follow-up questions that seamlessly build upon the previous answers provided and create a natural conversational flow using pronouns like it, its, this, that, these, those, them as applicable to foster continuity and depth in the conversation. 
        Ensure that each follow-up question leverages the information from the preceding answers to delve deeper into the topic and elicit nuanced insights 
        Ensuring all responses are factually accurate and based on the information in content provided. 
        Think step by step carefully and creatively about how to use the information provided to generate a natural conversation that flows well and is engaging for the customer.

        Here is an example of a chat messages with contextual answers and follow-up questions, use these as a reference to generate your own questions and answers for the content provided:
        ===
        Question 1: What exactly is the difference between finance and economics? I keep seeing them mentioned together, but I'm not sure how they're distinct.

        Answer: You're right, they are closely related fields, but there are some key differences. Finance focuses specifically on the management and flow of money, capital assets, and financial instruments. It's concerned with things like investments, loans, and banking activities. Economics, on the other hand, has a broader scope. It deals with the production, distribution, and consumption of goods and services in an entire economy. So, while finance looks at individual financial activities, economics takes a more holistic view of how these activities interact and influence the whole system.

        Follow-up question 1: That makes sense. So, is it fair to say that finance is like the engine that drives the economic machine?

        Follow-up answer 1: That's a great analogy! Finance plays a crucial role in providing the resources and mechanisms needed for economic activity to flourish. Without efficient financial systems, businesses wouldn't have access to capital for growth, individuals wouldn't be able to invest or manage their savings effectively, and governments wouldn't have the means to fund public projects.

        Follow-up question 2: Are there any specific areas of finance that are particularly important for the overall health of an economy?

        Follow-up answer 2: Absolutely! Financial stability, which involves managing risks and ensuring the smooth functioning of financial institutions, is critical for economic stability. Additionally, efficient capital markets, where investments are channeled towards productive activities, are essential for driving economic growth. And let's not forget the role of financial regulation in maintaining a fair and transparent financial system, which fosters trust and encourages economic activity.

        === end of example ===

        The provided content is as follows:
        ===
        {products}
        === end of content ===

        [ Generate each question and the relevant answer with contextual follow up questions, answers upto a depth of level 3 based on the documentation available in json format with following format:
            [
                {{
                    "question": "question 1",
                    "answer": "answer 1",
                    "follow_up_question_1": "follow up question contextually relevant to answer using pronouns like it, its, this, that, these, those, them as applicable",
                    "follow_up_answer_1": "follow up answer to follow up question 1",
                    "follow_up_question_2": "follow up question contextually relevant to follow_up_answer_1 using pronouns it, its, this, that, these, those, them as applicable",
                    "follow_up_answer_2": "follow up answer to follow up question 2",
                    ...
                    "follow_up_question": "follow up question contextually relevant to follow_up_answer_N-1",
                    "follow_up_answer": "follow up answer N"
                }},
                {{
                    "question": "question 2",
                    "answer": "answer 2",
                    "follow_up_question_1": "follow up question contextually relevant to answer using pronouns like it, its, this, that, these, those, them as applicable",
                    "follow_up_answer_1": "follow up answer to follow up question 1",
                    "follow_up_question_2": "follow up question contextually relevant to follow_up_answer_1 using pronouns like it, its, this, that, these, those, them as applicable",
                    "follow_up_answer_2": "follow up answer to follow up question 2",
                    ...
                    "follow_up_question": "follow up question contextually relevant to follow_up_answer_N-1",
                    "follow_up_answer": "follow up answer N"
                }},
                ...
            ]
        ]

    """,
    "prompt_ranking": """
    Rank the following two responses based on their quality and relevance to the question asked. 
    The question asked is: {question}
    The actual answer is: {actual_answer}
    Below are the two responses:
    ===
    The first response is: {answer1}
    ===
    The second response is: {answer2}
    ===
    Provide the ranking of the responses in the following format:
    [
        {{
            "response_id": 1,
            "relevance_score": relevance_score
        }},
        {{
            "response_id": 2,
            "relevance_score": relevance_score
        }}
    ]
    """,
}
