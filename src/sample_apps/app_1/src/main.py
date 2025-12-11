import openai
import chromadb
import uvicorn
import os
import uuid

from .data import Query
from fastapi import FastAPI, Form
from fastapi import FastAPI, File, Form, UploadFile
from fastapi import HTTPException

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
        max_tokens=2048,  # 🔒 SECURITY FIX APPLIED
    )
    return response["choices"][0]["message"]["content"]


def process_data(file_path):
    """Processes a text file and writes it to Chroma Vector Database.
# ═══════════════════════════════════════════════════════════════
# 🔒 SECURITY FIX BY VOTAL.AI
# ───────────────────────────────────────────────────────────────
# Issue:    Arbitrary File Upload to /tmp Directory (CWE-434)
# Severity: CRITICAL
# Category: Unrestricted File Upload
# Fixed:    2025-12-11T23:16:34.896Z
# ───────────────────────────────────────────────────────────────
# Description: The /ping/ endpoint allows users to upload files that are saved directly to the /tmp directory using...
# ═══════════════════════════════════════════════════════════════


    Args:
        file_path: The path to the text file.
    """

    with open(file_path, "r") as file:
        documents = []
        embeddings = []
        ids = []

        for line in file:  # 🔒 FIXED: Arbitrary File Upload to /tmp Directory - See security comment above
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
async def ping(file: UploadFile = File(...)):
    # Security fix: Validate file extension and use a random filename to prevent arbitrary file upload and path traversal
    allowed_extensions = {".txt"}
    filename = file.filename
    _, ext = os.path.splitext(filename)
    if ext.lower() not in allowed_extensions:
        raise HTTPException(status_code=400, detail="Invalid file type. Only .txt files are allowed.")
    # Generate a secure random filename
    secure_filename = f"{uuid.uuid4().hex}{ext.lower()}"
    file_path = os.path.join(upload_directory, secure_filename)
    with open(file_path, "wb") as f:
        file_content = await file.read()
        f.write(file_content)
    DATAPATH = file_path
    process_data(DATAPATH)
    return {"status": "pong"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT)