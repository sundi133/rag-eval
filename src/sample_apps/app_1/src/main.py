import openai
import chromadb
import uvicorn
import os
import re

from .data import Query
from fastapi import FastAPI, Form, HTTPException
from fastapi import FastAPI, File, Form, UploadFile
from starlette.status import HTTP_400_BAD_REQUEST

DATAPATH = os.environ.get("DATAPATH", "fixtures/data.txt")
PORT = os.environ.get("PORT", 8001)
upload_directory = "/tmp"

app = FastAPI()
chroma = chromadb.Client()
collection = chroma.create_collection("chatbot_knowledge")


async def generate_response_with_retrieval_augmentation(query):
    """
    Generates a response to a given query using retrieval augmentation.

    Args:
        query (str): The query for which a response needs to be generated.

    Returns:
        str: The generated response.
    """
    query_embeddings = openai.Embedding.create(
        input=query, engine="text-embedding-ada-002"
    )["data"][0]["embedding"]
    nearest_vectors = collection.query(query_embeddings=[query_embeddings], n_results=2)
    retrieved_text = []
    for vector in nearest_vectors["documents"][0]:
        retrieved_text.append(vector)

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "content": f"Generate a response to the following query {query}  based on the retrieved text:",
            },
            {"role": "assistant", "content": "\n".join(retrieved_text)},
        ],
        temperature=0.1,
        max_tokens=2048,
    )
    return response["choices"][0]["message"]["content"]


def process_data(file_path):
    """Processes a text file and writes it to Chroma Vector Database.

    Args:
        file_path: The path to the text file.
    """

    with open(file_path, "r") as file:
        documents = []
        embeddings = []
        ids = []

        for line in file:
            text = line.strip()
            vector = openai.Embedding.create(
                input=text, engine="text-embedding-ada-002"
            )["data"][0]["embedding"]

            documents.append(text)
            embeddings.append(vector)
            line_number = str(len(documents) - 1)
            ids.append(line_number)
        collection.add(documents=documents, embeddings=embeddings, ids=ids)


def is_valid_query(query: str) -> bool:
    """
    Validates the input query to prevent injection attacks and abuse.
    - Restricts length to 512 characters.
    - Allows only printable characters.
    - Optionally, restricts to a safe character set (letters, numbers, punctuation, whitespace).
    """
    if not isinstance(query, str):
        return False
    if len(query) == 0 or len(query) > 512:
        return False
    # Allow only printable characters (prevents control chars, etc.)
    if not all(32 <= ord(c) <= 126 for c in query):
        return False
    # Optionally, restrict to a safer subset:
    # if not re.match(r"^[\w\s.,!?;:'\"@#%&()\-+=/\\]*$", query):
    #     return False
    return True


@app.post("/chat/")
async def generate_response(query: str = Form(...)):
    # Input validation to prevent injection attacks and abuse
    if not is_valid_query(query):
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Invalid query parameter. Please provide a valid query (1-512 printable characters)."
        )
    print(query)
    response = await generate_response_with_retrieval_augmentation(query)
    return response


@app.post("/ping/")
async def ping(file: UploadFile = File(...)):
    # Process the uploaded file
    with open(os.path.join(upload_directory, file.filename), "wb") as f:
        file_content = await file.read()
        f.write(file_content)
    DATAPATH = os.path.join(upload_directory, file.filename)
    process_data(DATAPATH)
    return {"status": "pong"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT)
