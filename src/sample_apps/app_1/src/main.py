import openai
import chromadb
import uvicorn
import os

from .data import Query
from fastapi import FastAPI, Form

DATAPATH = os.environ.get("DATAPATH", "fixtures/data.txt")
PORT = os.environ.get("PORT", 8001)

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


@app.post("/chat/")
async def generate_response(query: str = Form(...)):
    print(query)
    response = await generate_response_with_retrieval_augmentation(query)
    return response


@app.post("/ping/")
async def ping():
    process_data(DATAPATH)
    return {"status": "pong"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT)
