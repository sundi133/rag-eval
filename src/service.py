import os
import uuid
import asyncio
import logging

from typing import List
from .generator import qa_generator
from .utils import (
    read_qa_data,
    read_endpoint_configurations,
    score_answer,
    get_llm_answer,
)
from pydantic import BaseModel, ValidationError
from fastapi.encoders import jsonable_encoder
from fastapi import status
from .ranking import evaluate_qa_data
from fastapi import FastAPI, File, Form, UploadFile, WebSocket, HTTPException, Depends
from fastapi.responses import JSONResponse
from fastapi.responses import FileResponse

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
ch = logging.StreamHandler()
ch.setFormatter(formatter)
logger.addHandler(ch)

app = FastAPI()
upload_directory = "/app/qa_generator_uploads"
output_directory = "/app/qa_generator_outputs"
if not os.path.exists(upload_directory):
    os.makedirs(upload_directory)
if not os.path.exists(output_directory):
    os.makedirs(output_directory)


@app.get("/")
def root():
    return {"status": "ok"}


@app.get("/health/")
def health():
    return {"status": "pong"}


@app.post("/generate/")
async def generator(
    data_path: str = Form(default="", max_length=1000, min_length=0),
    number_of_questions: int = Form(default=2, ge=1, le=1000),
    sample_size: int = Form(default=2, ge=1, le=1000),
    products_group_size: int = Form(default=1, ge=1, le=1000),
    group_columns: str = Form(default=""),  # ex - brand,category,gender
    model_name: str = Form(default="gpt-3.5-turbo"),
    prompt_key: str = Form(default="prompt_key_readme"),
    llm_type: str = Form(default=".txt"),
    generator_type: str = Form(default="text"),
    metadata: str = Form(default=""),
    crawl_depth: int = Form(default=1, ge=1, le=10),
    file: List[UploadFile] = File([]),
):
    if file and file[0] and hasattr(file[0], "filename"):
        with open(os.path.join(upload_directory, file[0].filename), "wb") as f:
            file_content = await file[0].read()
            f.write(file_content)
        if data_path == "":  # non empty if html links are provided
            data_path = os.path.join(upload_directory, file[0].filename)
    else:
        if data_path == "":
            return {"message": "No file or resource link provided as data source"}
    if llm_type == ".ner":
        generator_type = "ner"
        metadata = data_path
    logger.info(f"Data path: {data_path}")
    logger.info(f"Number of questions: {number_of_questions}")
    logger.info(f"Sample size: {sample_size}")
    logger.info(f"Products group size: {products_group_size}")
    logger.info(f"Group columns: {group_columns}")
    logger.info(f"Model name: {model_name}")
    logger.info(f"Prompt key: {prompt_key}")
    logger.info(f"LLM type: {llm_type}")
    logger.info(f"Generator type: {generator_type}")
    logger.info(f"Metadata: {metadata}")
    logger.info(f"Crawl depth: {crawl_depth}")
    gen_id = uuid.uuid4().hex
    output_file = os.path.join(output_directory, f"{gen_id}.json")
    logger.info(f"Output file: {output_file}")
    grouped_columns = []
    if group_columns:
        for column in group_columns.split(","):
            grouped_columns.append(column)
    asyncio.create_task(
        qa_generator(
            data_path,
            number_of_questions,
            sample_size,
            products_group_size,
            grouped_columns,
            output_file,
            model_name,
            prompt_key,
            llm_type,
            generator_type,
            metadata,
            crawl_depth,
        )
    )
    return JSONResponse(
        content={
            "message": "Generator in progress, Use the /download/ endpoint to check the status of the generator",
            "gen_id": gen_id,
        }
    )


@app.get("/download/{gen_id}")
async def download(gen_id: str):
    """
    Downloads a dataset with the given `gen_id` and returns a FileResponse object if the dataset exists.
    If the dataset does not exist, returns a dictionary with a "message" key and a corresponding error message.
    """
    output_file = os.path.join(output_directory, f"{gen_id}.json")
    logger.info(f"Output file: {output_file}")
    if os.path.exists(output_file):
        return FileResponse(
            output_file,
            headers={"Content-Disposition": f"attachment; filename={output_file}"},
        )
    else:
        return {"message": "Dataset not found"}


@app.post("/evaluate/")
async def evaluate(
    gen_id: str = Form(...),
    llm_endpoint: str = Form(...),
    log_wandb: bool = Form(default=False),
    sampling_factor: float = Form(default=1.0, ge=0.0, le=1.0),
):
    if not gen_id:
        raise HTTPException(status_code=400, detail="gen_id is required")

    qa_file = os.path.join(output_directory, f"{gen_id}.json")
    logger.info(f"Output file: {qa_file}")

    if os.path.exists(qa_file) and os.path.getsize(qa_file) > 0:
        endpoint_configs = [{"name": f"llm-f{gen_id}", "url": llm_endpoint}]
        output_file = os.path.join(output_directory, f"ranked_{gen_id}.json")
        await evaluate_qa_data(
            qa_file, endpoint_configs, log_wandb, output_file, sampling_factor
        )
        return JSONResponse(
            content={
                "message": "Ranker is complete, Use the /ranking/id endpoint to download evaluated ranked reports for each question",
                "gen_id": gen_id,
            }
        )
    else:
        return {"message": "Dataset with id {gen_id} not found"}


@app.get("/ranking/{gen_id}")
async def ranked_reports(gen_id: str):
    """
    Downloads a dataset with the given `gen_id` and returns a FileResponse object if the dataset exists.
    If the dataset does not exist, returns a dictionary with a "message" key and a corresponding error message.
    """
    output_file = os.path.join(output_directory, f"ranked_{gen_id}.json")
    if os.path.exists(output_file):
        return FileResponse(
            output_file,
            headers={"Content-Disposition": f"attachment; filename={output_file}"},
        )
    else:
        return {"message": "Ranked dataset not found"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    for i in range(10):
        await websocket.send_text(f"Streamed message {i}")
        await asyncio.sleep(1)  # Simulate a delay between messages
