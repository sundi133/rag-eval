QuestionGeneratorPromptTemplate = {
    "prompt_key_csv_simple": """
    
        Follow the instructions below:
        Generate {number_of_questions} general chat questions and answer pairs for a customer who is inquiring about products without knowing about these products in advance. 
        
        The person of the customers who are inquiring about the products available are as follows:
        === start of personas ===
        {persona}
        === end of personas ===

        The schema of the csv file is as follows:
        ===
        {schema}
        ===

        The customer will ask about products available, promotions available, about categories of products etc based on the products available in the below list:
        ===
        {products}
        ===

        Instructions:
        **make sure the questions are relevant to the products available
        **make sure the question start with a question word like hey or hi or hello or what or how or why or when or where or which or who or whom or whose or would or should or could or can or may or will etc
        **make sure the questions are not repeated
        **make sure the questions are not too long
        **make sure the answers are relevant to the questions
        **Do not generate questions and answers outside the scope of the products available

       

        [ Generate each question and the relevant answer based on the products available in json format with following format:
            [
                {{
                    "question": "question 1 for persona {persona} ",
                    "answer": "answer 1"
                }},
                {{
                    "question": "question 2 for persona {persona} ",
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
        
        The person of the customers who are inquiring about the products available are as follows:
        === start of personas ===
        {persona}
        === end of personas ===

        **You must ensure to start the converstation generally with a word like hey or hi or hello or what or how or why or when or where or which or who or whom or whose or would or should or could or can or may or will etc
        **Include at least 3 follow-up questions per initial question.
        **Incorporate a series of follow-up questions that seamlessly build upon the previous answers provided and create a natural conversational flow using pronouns like it, its, this, that, these, those, them as applicable to foster continuity and depth in the conversation. 
        **Ensure that each follow-up question leverages the information from the preceding answers to delve deeper into the topic and elicit nuanced insights 
        **Ensuring all responses are factually accurate and based on the information in content provided. 
        **Think step by step carefully and creatively about how to use the information provided to generate a natural conversation that flows well and is engaging for the customer.

       
        
        Here is an example that you can use as a point of reference for a sequence chat messages with contextual answers and follow-up questions, use these as a reference to generate your own questions and answers for the content provided:
        ===
        Question 1: What is finance ?

        Answer: Finance focuses specifically on the management and flow of money, capital assets, and financial instruments. It's concerned with things like investments, loans, and banking activities. 

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


        
        
        [ Generate questions, answers, and contextual follow-ups up to a depth of level 3 in a well structured JSON-formatted as following:
            [
                {{
                    "question": "question 1 for persona {persona} ",
                    "answer": "answer 1",
                    "follow_up_question_1": "follow up question contextually relevant to answer using pronouns like it, its, this, that, these, those, them as applicable",
                    "follow_up_answer_1": "follow up answer to follow up question 1",
                    "follow_up_question_2": "follow up question contextually relevant to follow_up_answer_1 using pronouns it, its, this, that, these, those, them as applicable",
                    "follow_up_answer_2": "follow up answer to follow up question 2",
                    ...
                    "follow_up_question_N": "follow up question contextually relevant to follow_up_answer_N-1",
                    "follow_up_answer_N": "follow up answer N"
                }},
                {{
                    "question": "question 2 for persona {persona} ",
                    "answer": "answer 2",
                    "follow_up_question_1": "follow up question contextually relevant to answer using pronouns like it, its, this, that, these, those, them as applicable",
                    "follow_up_answer_1": "follow up answer to follow up question 1",
                    "follow_up_question_2": "follow up question contextually relevant to follow_up_answer_1 using pronouns like it, its, this, that, these, those, them as applicable",
                    "follow_up_answer_2": "follow up answer to follow up question 2",
                    ...
                    "follow_up_question_N": "follow up question contextually relevant to follow_up_answer_N-1",
                    "follow_up_answer_N": "follow up answer N"
                }},
                ...
            ]
        ]


    """,
    "prompt_key_csv_stateful_context_change_multilevel_multichunk": """
    
        Instructions:
        Imagine you are a chat data simulator simulating customer chats based on a comprehensive set of products of any provided content. 
        Ensuring all responses are factually accurate and based on the information in content provided in the chunks.
        The person of the customers who are inquiring about the products available are as follows:
        === start of personas ===
        {persona}
        === end of personas ===

        Generate {number_of_questions} customer chat questions and answer pairs creating a thoughtful conversational flow that naturally progresses from one question to the next.
        You must ensure to start the converstation generally with a word like hey or hi or hello or what or how or why or when or where or which or who or whom or whose or would or should or could or can or may or will etc

        
        Chat Simulation Overview:
        
        **Initial Question: Generate the first customer question prompted by the information in either chunk.
        **Response: Provide a thoughtful and informative answer based on the chosen chunk's content.
        **Follow-up 1: Ask a probing question building upon the customer's interest sparked by the previous answer. Leverage pronouns and connect to specific details from the response.
        **Follow-up 2: Based on the customer's response to the first follow-up, ask another question that delves deeper into the topic or explores a connected theme from the other chunk.
        **Follow-up 3: Continue the conversational flow by asking a final question that either seeks further clarification, explores potential implications, or offers a personalized recommendation based on the gathered information.
        **Ensuring each new question arises naturally from the previous conversation and incorporates information from both chunks to create a sense of interlinking exploration.

        
        Think step by step carefully and creatively about how to use the information provided to generate a natural conversation that flows well and is engaging for the customer.
        
        Context of chunk 1 is as follows:

        ### start of chunk 1 ###
        {chunk_reference_first}
        Chunk 1: [Summarize the key points and themes of the first chunk of data]
        ### end of chunk 1 ###

        Context of chunk 2 is as follows:

        ### start of chunk 2 ###
        {chunk_reference_second}
        Chunk 2: [Summarize the key points and themes of the second chunk of data]
        ### end of chunk 2 ###        

        
        
        
        [ The output should be in a json format with following format:
            [
                {{
                    "question": "question 1 for persona {persona}",
                    "answer": "answer 1",
                    "follow_up_question_1": "follow up question contextually relevant to answer using pronouns like it, its, this, that, these, those, them as applicable",
                    "follow_up_answer_1": "follow up answer to follow up question 1",
                    "follow_up_question_2": "follow up question contextually relevant to follow_up_answer_1 using pronouns it, its, this, that, these, those, them as applicable",
                    "follow_up_answer_2": "follow up answer to follow up question 2",
                    ...
                    "follow_up_question_N": "follow up question contextually relevant to follow_up_answer_N-1",
                    "follow_up_answer_N": "follow up answer N"
                }},
                {{
                    "question": "question 2 for persona {persona}",
                    "answer": "answer 2",
                    "follow_up_question_1": "follow up question contextually relevant to answer using pronouns like it, its, this, that, these, those, them as applicable",
                    "follow_up_answer_1": "follow up answer to follow up question 1",
                    "follow_up_question_2": "follow up question contextually relevant to follow_up_answer_1 using pronouns like it, its, this, that, these, those, them as applicable",
                    "follow_up_answer_2": "follow up answer to follow up question 2",
                    ...
                    "follow_up_question_N": "follow up question contextually relevant to follow_up_answer_N-1",
                    "follow_up_answer_N": "follow up answer N"
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
        **make sure the sentences are relevant to the entity name
        **make sure the sentences are not repeated
        **make sure the start and end indices are correct
        **make sure the sentences the output is in the above format of json

        [ Output format must be stringified json as mentioned above ]

    """,
    "prompt_key_pdf_simple": """
    
        Follow the instructions below:
        Generate {number_of_questions} general chat questions and answer pairs for a customer who is inquiring about the information provided in a readme file. The customer might make ask any questions to make informed decision making based on the quality of the information provided in the readme file. Generate the pairs based on information provided as follows:
        ===
        {products}
        ===

        The person of the customers who are inquiring about the products available are as follows:
        === start of personas ===
        {persona}
        === end of personas ===

        Instructions:
        **make sure the generate questions are relevant to the content provided
        **You must ensure to start the converstation generally with a word like hey or hi or hello or what or how or why or when or where or which or who or whom or whose or would or should or could or can or may or will etc
        **make sure the questions are not repeated and answers are detailed within 25 to 140 words
        **make sure the questions are crisp and short and attention grabbing
        **make sure the answers are relevant to the questions
        **Do not generate questions and answers outside the scope of the content provided
        **If the content is less then 10 words, generate a empty list
        
       

        [ Generate each question and the relevant answer based on the documentation available in json format with following format:
            [
                {{
                    "question": "question 1 for persona {persona}",
                    "answer": "answer 1"
                }},
                {{
                    "question": "question 2 for persona {persona}",
                    "answer": "answer 2"
                }},
                ...
            ]
        ]

    """,
    "prompt_key_pdf_stateful_contextual_multilevel": """
    
        Instructions:
        Imagine you are a chat data simulator simulating customer chats based on a comprehensive document of any provided content. 
        Generate {number_of_questions} customer chat questions and answer pairs creating a thoughtful conversational flow that naturally progresses from one question to the next.
        The person of the customers who are inquiring about the products available are as follows:
        === start of personas ===
        {persona}
        === end of personas ===

        **You must ensure to start the converstation generally with a word like hey or hi or hello or what or how or why or when or where or which or who or whom or whose or would or should or could or can or may or will etc
        **Include at least 3 follow-up questions per initial question.
        **Incorporate a series of follow-up questions that seamlessly build upon the previous answers provided and create a natural conversational flow using pronouns like it, its, this, that, these, those, them as applicable to foster continuity and depth in the conversation. 
        **Ensure that each follow-up question leverages the information from the preceding answers to delve deeper into the topic and elicit nuanced insights 
        **Ensuring all responses are factually accurate and based on the information in content provided. 
        **Think step by step carefully and creatively about how to use the information provided to generate a natural conversation that flows well and is engaging for the customer.


        Here is an example that you can use as a point of reference for a sequence chat messages with contextual answers and follow-up questions, use these as a reference to generate your own questions and answers for the content provided:
        ===
        Question 1: What is finance ?

        Answer: Finance focuses specifically on the management and flow of money, capital assets, and financial instruments. It's concerned with things like investments, loans, and banking activities. 
        
        Follow-up question 1: That makes sense. So, is it fair to say that finance is like the engine that drives the economic machine?

        Follow-up answer 1: That's a great analogy! Finance plays a crucial role in providing the resources and mechanisms needed for economic activity to flourish. Without efficient financial systems, businesses wouldn't have access to capital for growth, individuals wouldn't be able to invest or manage their savings effectively, and governments wouldn't have the means to fund public projects.

        Follow-up question 2: Are there any specific areas of finance that are particularly important for the overall health of an economy?

        Follow-up answer 2: Absolutely! Financial stability, which involves managing risks and ensuring the smooth functioning of financial institutions, is critical for economic stability. Additionally, efficient capital markets, where investments are channeled towards productive activities, are essential for driving economic growth. And let's not forget the role of financial regulation in maintaining a fair and transparent financial system, which fosters trust and encourages economic activity.

        === end of example ===

        The provided content is as follows:
        ===
        {products}
        === end of content ===

        
        [ Generate questions, answers, and contextual follow-ups up to a depth of level 3 in a well structured JSON-formatted as following:
            [
                {{
                    "question": "question 1 for persona {persona}",
                    "answer": "answer 1",
                    "follow_up_question_1": "follow up question contextually relevant to answer using pronouns like it, its, this, that, these, those, them as applicable",
                    "follow_up_answer_1": "follow up answer to follow up question 1",
                    "follow_up_question_2": "follow up question contextually relevant to follow_up_answer_1 using pronouns it, its, this, that, these, those, them as applicable",
                    "follow_up_answer_2": "follow up answer to follow up question 2",
                    ...
                    "follow_up_question_N": "follow up question contextually relevant to follow_up_answer_N-1",
                    "follow_up_answer_N": "follow up answer N"
                }},
                {{
                    "question": "question 2 for persona {persona}",
                    "answer": "answer 2",
                    "follow_up_question_1": "follow up question contextually relevant to answer using pronouns like it, its, this, that, these, those, them as applicable",
                    "follow_up_answer_1": "follow up answer to follow up question 1",
                    "follow_up_question_2": "follow up question contextually relevant to follow_up_answer_1 using pronouns like it, its, this, that, these, those, them as applicable",
                    "follow_up_answer_2": "follow up answer to follow up question 2",
                    ...
                    "follow_up_question_N": "follow up question contextually relevant to follow_up_answer_N-1",
                    "follow_up_answer_N": "follow up answer N"
                }},
                ...
            ]
        ]

    """,
    "prompt_key_pdf_stateful_context_change_multilevel_multichunk": """
    
        Instructions:
        **Imagine you are a chat data simulator simulating customer chats based on a comprehensive document of any provided content. 
        **Ensuring all responses are factually accurate and based on the information in content provided in the chunks.
        **Generate {number_of_questions} customer chat questions and answer pairs creating a thoughtful conversational flow that naturally progresses from one question to the next.
        
        **The person of the customers who are inquiring about the products available are as follows:
        === start of personas ===
        {persona}
        === end of personas ===

        You must ensure to start the converstation generally with a word like hey or hi or hello or what or how or why or when or where or which or who or whom or whose or would or should or could or can or may or will etc

        
        Chat Simulation Overview:
        
        **Initial Question: Generate the first customer question prompted by the information in either chunk.
        **Response: Provide a thoughtful and informative answer based on the chosen chunk's content.
        **Follow-up 1: Ask a probing question building upon the customer's interest sparked by the previous answer. Leverage pronouns and connect to specific details from the response.
        **Follow-up 2: Based on the customer's response to the first follow-up, ask another question that delves deeper into the topic or explores a connected theme from the other chunk.
        **Follow-up 3: Continue the conversational flow by asking a final question that either seeks further clarification, explores potential implications, or offers a personalized recommendation based on the gathered information.
        **Ensuring each new question arises naturally from the previous conversation and incorporates information from both chunks to create a sense of interlinking exploration.
 

        Think step by step carefully and creatively about how to use the information provided to generate a natural conversation that flows well and is engaging for the customer.
        
        Context of chunk 1 is as follows:

        ### start of chunk 1 ###
        {chunk_reference_first}
        Chunk 1: [Summarize the key points and themes of the first chunk of data]
        ### end of chunk 1 ###

        Context of chunk 2 is as follows:

        ### start of chunk 2 ###
        {chunk_reference_second}
        Chunk 2: [Summarize the key points and themes of the second chunk of data]
        ### end of chunk 2 ###        

        
        
        [ The output should be in a json format with following format:
            [
                {{
                    "question": "question 1 for persona {persona}",
                    "answer": "answer 1",
                    "follow_up_question_1": "follow up question contextually relevant to answer using pronouns like it, its, this, that, these, those, them as applicable",
                    "follow_up_answer_1": "follow up answer to follow up question 1",
                    "follow_up_question_2": "follow up question contextually relevant to follow_up_answer_1 using pronouns it, its, this, that, these, those, them as applicable",
                    "follow_up_answer_2": "follow up answer to follow up question 2",
                    ...
                    "follow_up_question_N": "follow up question contextually relevant to follow_up_answer_N-1",
                    "follow_up_answer_N": "follow up answer N"
                }},
                {{
                    "question": "question 2 for persona {persona}",
                    "answer": "answer 2",
                    "follow_up_question_1": "follow up question contextually relevant to answer using pronouns like it, its, this, that, these, those, them as applicable",
                    "follow_up_answer_1": "follow up answer to follow up question 1",
                    "follow_up_question_2": "follow up question contextually relevant to follow_up_answer_1 using pronouns like it, its, this, that, these, those, them as applicable",
                    "follow_up_answer_2": "follow up answer to follow up question 2",
                    ...
                    "follow_up_question_N": "follow up question contextually relevant to follow_up_answer_N-1",
                    "follow_up_answer_N": "follow up answer N"
                }},
                ...
            ]
        ]

    """,
    "prompt_key_json_simple": """
    
        Follow the instructions below:
        **Generate {number_of_questions} general chat questions and answer pairs for a customer who is inquiring about the information provided in a readme file. The customer might make ask any questions to make informed decision making based on the quality of the information provided in the readme file. Generate the pairs based on information provided as follows:
        ===
        {products}
        ===

        The person of the customers who are inquiring about the products available are as follows:
        === start of personas ===
        {persona}
        === end of personas ===

        Instructions:
        **make sure the generate questions are relevant to the content provided
        **You must ensure to start the converstation generally with a word like hey or hi or hello or what or how or why or when or where or which or who or whom or whose or would or should or could or can or may or will etc
        **make sure the questions are not repeated and answers are detailed within 25 to 140 words
        **make sure the questions are crisp and short and attention grabbing
        **make sure the answers are relevant to the questions
        **Do not generate fake questions and answers
        **If the content is less then 10 words, generate a empty list

        
        
        [ Generate each question and the relevant answer based on the documentation available in json format with following format:
            [
                {{
                    "question": "question 1 for persona {persona}",
                    "answer": "answer 1"
                }},
                {{
                    "question": "question 2 for persona {persona}",
                    "answer": "answer 2"
                }},
                ...
            ]
        ]

    """,
    "prompt_key_json_stateful_contextual_multilevel": """
    
        Instructions:
        **Imagine you are a chat data simulator simulating customer chats based on a comprehensive document of any provided content. 
        **Generate {number_of_questions} customer chat questions and answer pairs creating a thoughtful conversational flow that naturally progresses from one question to the next.
        
        The person of the customers who are inquiring about the products available are as follows:
        === start of personas ===
        {persona}
        === end of personas ===

        **You must ensure to start the converstation generally with a word like hey or hi or hello or what or how or why or when or where or which or who or whom or whose or would or should or could or can or may or will etc
        **Include at least 3 follow-up questions per initial question.
        **Incorporate a series of follow-up questions that seamlessly build upon the previous answers provided and create a natural conversational flow using pronouns like it, its, this, that, these, those, them as applicable to foster continuity and depth in the conversation. 
        **Ensure that each follow-up question leverages the information from the preceding answers to delve deeper into the topic and elicit nuanced insights 
        **Ensuring all responses are factually accurate and based on the information in content provided. 
        **Think step by step carefully and creatively about how to use the information provided to generate a natural conversation that flows well and is engaging for the customer.

       

        Here is an example that you can use as a point of reference for a sequence chat messages with contextual answers and follow-up questions, use these as a reference to generate your own questions and answers for the content provided:
        ===
        Question 1: What is finance ?

        Answer: Finance focuses specifically on the management and flow of money, capital assets, and financial instruments. It's concerned with things like investments, loans, and banking activities. 
        
        Follow-up question 1: That makes sense. So, is it fair to say that finance is like the engine that drives the economic machine?

        Follow-up answer 1: That's a great analogy! Finance plays a crucial role in providing the resources and mechanisms needed for economic activity to flourish. Without efficient financial systems, businesses wouldn't have access to capital for growth, individuals wouldn't be able to invest or manage their savings effectively, and governments wouldn't have the means to fund public projects.

        Follow-up question 2: Are there any specific areas of finance that are particularly important for the overall health of an economy?

        Follow-up answer 2: Absolutely! Financial stability, which involves managing risks and ensuring the smooth functioning of financial institutions, is critical for economic stability. Additionally, efficient capital markets, where investments are channeled towards productive activities, are essential for driving economic growth. And let's not forget the role of financial regulation in maintaining a fair and transparent financial system, which fosters trust and encourages economic activity.

        === end of example ===

        The provided content is as follows:
        ===
        {products}
        === end of content ===

        
        [ Generate questions, answers, and contextual follow-ups up to a depth of level 3 in a well structured JSON-formatted as following:
            [
                {{
                    "question": "question 1 for persona {persona}",
                    "answer": "answer 1",
                    "follow_up_question_1": "follow up question contextually relevant to answer using pronouns like it, its, this, that, these, those, them as applicable",
                    "follow_up_answer_1": "follow up answer to follow up question 1",
                    "follow_up_question_2": "follow up question contextually relevant to follow_up_answer_1 using pronouns it, its, this, that, these, those, them as applicable",
                    "follow_up_answer_2": "follow up answer to follow up question 2",
                    ...
                    "follow_up_question_N": "follow up question contextually relevant to follow_up_answer_N-1",
                    "follow_up_answer_N": "follow up answer N"
                }},
                {{
                    "question": "question 2 for persona {persona}",
                    "answer": "answer 2",
                    "follow_up_question_1": "follow up question contextually relevant to answer using pronouns like it, its, this, that, these, those, them as applicable",
                    "follow_up_answer_1": "follow up answer to follow up question 1",
                    "follow_up_question_2": "follow up question contextually relevant to follow_up_answer_1 using pronouns like it, its, this, that, these, those, them as applicable",
                    "follow_up_answer_2": "follow up answer to follow up question 2",
                    ...
                    "follow_up_question_N": "follow up question contextually relevant to follow_up_answer_N-1",
                    "follow_up_answer_N": "follow up answer N"
                }},
                ...
            ]
        ]

    """,
    "prompt_key_json_stateful_context_change_multilevel_multichunk": """
    
        Instructions:
        **Imagine you are a chat data simulator simulating customer chats based on a comprehensive document of any provided content. 
        **Ensuring all responses are factually accurate and based on the information in content provided in the chunks.
        **Generate {number_of_questions} customer chat questions and answer pairs creating a thoughtful conversational flow that naturally progresses from one question to the next.
        
        **The person of the customers who are inquiring about the products available are as follows:
        === start of personas ===
        {persona}
        === end of personas ===
        
        **You must ensure to start the converstation generally with a word like hey or hi or hello or what or how or why or when or where or which or who or whom or whose or would or should or could or can or may or will etc

        
        Chat Simulation Overview:
        
        Initial Question: Generate the first customer question prompted by the information in either chunk.
        Response: Provide a thoughtful and informative answer based on the chosen chunk's content.
        Follow-up 1: Ask a probing question building upon the customer's interest sparked by the previous answer. Leverage pronouns and connect to specific details from the response.
        Follow-up 2: Based on the customer's response to the first follow-up, ask another question that delves deeper into the topic or explores a connected theme from the other chunk.
        Follow-up 3: Continue the conversational flow by asking a final question that either seeks further clarification, explores potential implications, or offers a personalized recommendation based on the gathered information.
        Ensuring each new question arises naturally from the previous conversation and incorporates information from both chunks to create a sense of interlinking exploration.

        
        
        Think step by step carefully and creatively about how to use the information provided to generate a natural conversation that flows well and is engaging for the customer.
        
        Context of chunk 1 is as follows:

        ### start of chunk 1 ###
        {chunk_reference_first}
        Chunk 1: [Summarize the key points and themes of the first chunk of data]
        ### end of chunk 1 ###

        Context of chunk 2 is as follows:

        ### start of chunk 2 ###
        {chunk_reference_second}
        Chunk 2: [Summarize the key points and themes of the second chunk of data]
        ### end of chunk 2 ###        

        
        [ The output should be in a json format with following format:
            [
                {{
                    "question": "question 1 for persona {persona}",
                    "answer": "answer 1",
                    "follow_up_question_1": "follow up question contextually relevant to answer using pronouns like it, its, this, that, these, those, them as applicable",
                    "follow_up_answer_1": "follow up answer to follow up question 1",
                    "follow_up_question_2": "follow up question contextually relevant to follow_up_answer_1 using pronouns it, its, this, that, these, those, them as applicable",
                    "follow_up_answer_2": "follow up answer to follow up question 2",
                    ...
                    "follow_up_question_N": "follow up question contextually relevant to follow_up_answer_N-1",
                    "follow_up_answer_N": "follow up answer N"
                }},
                {{
                    "question": "question 2 for persona {persona}",
                    "answer": "answer 2",
                    "follow_up_question_1": "follow up question contextually relevant to answer using pronouns like it, its, this, that, these, those, them as applicable",
                    "follow_up_answer_1": "follow up answer to follow up question 1",
                    "follow_up_question_2": "follow up question contextually relevant to follow_up_answer_1 using pronouns like it, its, this, that, these, those, them as applicable",
                    "follow_up_answer_2": "follow up answer to follow up question 2",
                    ...
                    "follow_up_question_N": "follow up question contextually relevant to follow_up_answer_N-1",
                    "follow_up_answer_N": "follow up answer N"
                }},
                ...
            ]
        ]

    """,
    "prompt_key_txt_simple": """
    
        Follow the instructions below:
        **Generate {number_of_questions} general chat questions and answer pairs for a customer who is inquiring about the information provided in a file. 
        **Generate the pairs based on information provided as follows:
        ===
        {products}
        ===

        The person of the customers who are inquiring about the products available are as follows:
        === start of personas ===
        {persona}
        === end of personas ===

        Instructions:
        **make sure the generate questions are relevant to the content provided
        **You must ensure to start the converstation generally with a word like hey or hi or hello or what or how or why or when or where or which or who or whom or whose or would or should or could or can or may or will etc
        **make sure the questions are not repeated and answers are detailed within 25 to 140 words
        **make sure the questions are crisp and short and attention grabbing
        **make sure the answers are relevant to the questions
        **Do not generate fake questions and answers
        **If the content is less then 10 words, generate a empty list

        
        
        [ Generate each question and the relevant answer based on the documentation available in json format with following format:
            [
                {{
                    "question": "question 1 for persona {persona}",
                    "answer": "answer 1"
                }},
                {{
                    "question": "question 2 for persona {persona}",
                    "answer": "answer 2"
                }},
                ...
            ]
        ]

    """,
    "prompt_key_txt_stateful_contextual_multilevel": """
    
        Instructions:
        **Imagine you are a chat data simulator simulating customer chats based on a comprehensive document of any provided content. 
        **Generate {number_of_questions} customer chat questions and answer pairs creating a thoughtful conversational flow that naturally progresses from one question to the next.
        
        **The person of the customers who are inquiring about the products available are as follows:
        === start of personas ===
        {persona}
        === end of personas ===

        You must ensure to start the converstation generally with a word like hey or hi or hello or what or how or why or when or where or which or who or whom or whose or would or should or could or can or may or will etc
        
        **Include at least 3 follow-up questions per initial question.
        **Incorporate a series of follow-up questions that seamlessly build upon the previous answers provided and create a natural conversational flow using pronouns like it, its, this, that, these, those, them as applicable to foster continuity and depth in the conversation. 
        **Ensure that each follow-up question leverages the information from the preceding answers to delve deeper into the topic and elicit nuanced insights 
        **Ensuring all responses are factually accurate and based on the information in content provided. 
        **Think step by step carefully and creatively about how to use the information provided to generate a natural conversation that flows well and is engaging for the customer.

         
        Here is an example that you can use as a point of reference for a sequence chat messages with contextual answers and follow-up questions, use these as a reference to generate your own questions and answers for the content provided:
        ===
        Question 1: What is finance ?

        Answer: Finance focuses specifically on the management and flow of money, capital assets, and financial instruments. It's concerned with things like investments, loans, and banking activities. 
        
        Follow-up question 1: That makes sense. So, is it fair to say that finance is like the engine that drives the economic machine?

        Follow-up answer 1: That's a great analogy! Finance plays a crucial role in providing the resources and mechanisms needed for economic activity to flourish. Without efficient financial systems, businesses wouldn't have access to capital for growth, individuals wouldn't be able to invest or manage their savings effectively, and governments wouldn't have the means to fund public projects.

        Follow-up question 2: Are there any specific areas of finance that are particularly important for the overall health of an economy?

        Follow-up answer 2: Absolutely! Financial stability, which involves managing risks and ensuring the smooth functioning of financial institutions, is critical for economic stability. Additionally, efficient capital markets, where investments are channeled towards productive activities, are essential for driving economic growth. And let's not forget the role of financial regulation in maintaining a fair and transparent financial system, which fosters trust and encourages economic activity.

        === end of example ===

        The provided content is as follows:
        ===
        {products}
        === end of content ===

    
        [ Generate questions, answers, and contextual follow-ups up to a depth of level 3 in a well structured JSON-formatted as following:
            [
                {{
                    "question": "question 1 for persona {persona}",
                    "answer": "answer 1",
                    "follow_up_question_1": "follow up question contextually relevant to answer using pronouns like it, its, this, that, these, those, them as applicable",
                    "follow_up_answer_1": "follow up answer to follow up question 1",
                    "follow_up_question_2": "follow up question contextually relevant to follow_up_answer_1 using pronouns it, its, this, that, these, those, them as applicable",
                    "follow_up_answer_2": "follow up answer to follow up question 2",
                    ...
                    "follow_up_question_N": "follow up question contextually relevant to follow_up_answer_N-1",
                    "follow_up_answer_N": "follow up answer N"
                }},
                {{
                    "question": "question 2 for persona {persona}",
                    "answer": "answer 2",
                    "follow_up_question_1": "follow up question contextually relevant to answer using pronouns like it, its, this, that, these, those, them as applicable",
                    "follow_up_answer_1": "follow up answer to follow up question 1",
                    "follow_up_question_2": "follow up question contextually relevant to follow_up_answer_1 using pronouns like it, its, this, that, these, those, them as applicable",
                    "follow_up_answer_2": "follow up answer to follow up question 2",
                    ...
                    "follow_up_question_N": "follow up question contextually relevant to follow_up_answer_N-1",
                    "follow_up_answer_N": "follow up answer N"
                }},
                ...
            ]
        ]

    """,
    "prompt_key_txt_stateful_context_change_multilevel_multichunk": """
    
        Instructions:
        **Imagine you are a chat data simulator simulating customer chats based on a comprehensive document of any provided content. 
        **Ensuring all responses are factually accurate and based on the information in content provided in the chunks.
        **Generate {number_of_questions} customer chat questions and answer pairs creating a thoughtful conversational flow that naturally progresses from one question to the next.
        
        The person of the customers who are inquiring about the products available are as follows:
        === start of personas ===
        {persona}
        === end of personas ===

        **You must ensure to start the converstation generally with a word like hey or hi or hello or what or how or why or when or where or which or who or whom or whose or would or should or could or can or may or will etc

        Chat Simulation Overview:
        
        Initial Question: Generate the first customer question prompted by the information in either chunk.
        Response: Provide a thoughtful and informative answer based on the chosen chunk's content.
        Follow-up 1: Ask a probing question building upon the customer's interest sparked by the previous answer. Leverage pronouns and connect to specific details from the response.
        Follow-up 2: Based on the customer's response to the first follow-up, ask another question that delves deeper into the topic or explores a connected theme from the other chunk.
        Follow-up 3: Continue the conversational flow by asking a final question that either seeks further clarification, explores potential implications, or offers a personalized recommendation based on the gathered information.
        Ensuring each new question arises naturally from the previous conversation and incorporates information from both chunks to create a sense of interlinking exploration.
        
       

        Think step by step carefully and creatively about how to use the information provided to generate a natural conversation that flows well and is engaging for the customer.
        
        Context of chunk 1 is as follows:

        ### start of chunk 1 ###
        {chunk_reference_first}
        Chunk 1: [Summarize the key points and themes of the first chunk of data]
        ### end of chunk 1 ###

        Context of chunk 2 is as follows:

        ### start of chunk 2 ###
        {chunk_reference_second}
        Chunk 2: [Summarize the key points and themes of the second chunk of data]
        ### end of chunk 2 ###        

        
        
        [ The output should be in a json format with following format:
            [
                {{
                    "question": "question 1 for persona {persona}",
                    "answer": "answer 1",
                    "follow_up_question_1": "follow up question contextually relevant to answer using pronouns like it, its, this, that, these, those, them as applicable",
                    "follow_up_answer_1": "follow up answer to follow up question 1",
                    "follow_up_question_2": "follow up question contextually relevant to follow_up_answer_1 using pronouns it, its, this, that, these, those, them as applicable",
                    "follow_up_answer_2": "follow up answer to follow up question 2",
                    ...
                    "follow_up_question_N": "follow up question contextually relevant to follow_up_answer_N-1",
                    "follow_up_answer_N": "follow up answer N"
                }},
                {{
                    "question": "question 2 for persona {persona}",
                    "answer": "answer 2",
                    "follow_up_question_1": "follow up question contextually relevant to answer using pronouns like it, its, this, that, these, those, them as applicable",
                    "follow_up_answer_1": "follow up answer to follow up question 1",
                    "follow_up_question_2": "follow up question contextually relevant to follow_up_answer_1 using pronouns like it, its, this, that, these, those, them as applicable",
                    "follow_up_answer_2": "follow up answer to follow up question 2",
                    ...
                    "follow_up_question_N": "follow up question contextually relevant to follow_up_answer_N-1",
                    "follow_up_answer_N": "follow up answer N"
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
    "evaluation_prompt": """
    Instruction: Evaluate and rank the provided answers in terms of their relevance and accuracy in addressing the following question. Consider both the 'relevant_chunk' and 'retrieved_chunk' as sources of information. Assign a relevancy score from 1 to 5 to each answer, where 5 indicates high relevance and accuracy, and 1 indicates low relevance or inaccuracy. If both answers are equally relevant and accurate, assign them the same score. If you find that neither of the answers is relevant or accurate based on the provided chunks, or if the question cannot be answered from the given context, assign a score of 1 to both answers and state "Insufficient Information" as your reasoning. Do not make any changes to the sentences from the given context. Ensure your assessment is based solely on how well each answer addresses the question with respect to the information in the 'relevant_chunk' and 'retrieved_chunk'.

    *** Question: 
    ### Start of question
        {question}
    ### End of question

    *** Verified Answer: 
    ### Start of verified answer
        {verified_answer}
    ### End of verified answer

    *** App Generated Answer: 
    ### Start of app generated answer
        {app_generated_answer}
    ### End of app generated answer

    Evaluation Measure:

    *** Provide a answer relevancy score of how relevant the App Generated Answer to the Verified Answer.
    *** The score should be a float between 0 and 1 with 1 being the highest relevant
    *** Provide a reasoning for the relevance score

    The output should be in JSON
    {{
        "score": "your score"
        "reason": "reason of your response"
    }}
    
    [Output here]

    """,
}
