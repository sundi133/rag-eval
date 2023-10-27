import os
import uuid
import asyncio

from .main import generator
from .utils import (
    read_qa_data,
    read_endpoint_configurations,
    score_answer,
    get_llm_answer,
)
from .ranking import evaluate_qa_data

from fastapi import FastAPI, File, Form, UploadFile, WebSocket
from fastapi.responses import JSONResponse
from fastapi.responses import FileResponse

app = FastAPI()
upload_directory = "qa_generator_uploads"
output_directory = "qa_generator_outputs"


@app.get("/")
def health():
    return {"status": "ok"}


@app.post("/generate/")
async def generator(
    file: UploadFile = File(...),
    data_path: str = "",
    number_of_questions: int = 10,
    sample_size: int = 10,
    products_group_size: int = 3,
    group_columns: str = "brand,sub_category,category,gender",
    model_name: str = "gpt-3.5-turbo",
    prompt_key: str = "prompt_key_readme",
    llm_type: str = ".txt",
    generator_type: str = "text",
    metadata_path: str = "",
    crawl_depth: int = 2,
):
    # Create the uploads directory if it doesn't exist
    if not os.path.exists(upload_directory):
        os.makedirs(upload_directory)
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Save the uploaded file
    with open(os.path.join(upload_directory, file.filename), "wb") as f:
        f.write(file.file.read())

    if data_path == "":
        data_path = os.path.join(upload_directory, file.filename)

    gen_id = uuid.uuid4().hex
    output_file = os.path.join(output_directory, f"{gen_id}.txt")

    await generator(
        data_path,
        number_of_questions,
        sample_size,
        products_group_size,
        group_columns,
        output_file,
        model_name,
        prompt_key,
        llm_type,
        generator_type,
        metadata_path,
        crawl_depth,
    )
    return JSONResponse(
        content={
            "message": "Generator in progress, Use the /download-qa-validation-pairs/gen_id endpoint to check the status of the generator",
            "gen_id": gen_id,
        }
    )


@app.get("/download-qa-pairs/{gen_id}")
async def download(gen_id: str):
    """
    Downloads a dataset with the given `gen_id` and returns a FileResponse object if the dataset exists.
    If the dataset does not exist, returns a dictionary with a "message" key and a corresponding error message.
    """
    output_file = os.path.join(output_directory, f"{gen_id}.txt")
    if os.path.exists(output_file):
        return FileResponse(
            output_file,
            headers={"Content-Disposition": f"attachment; filename={output_file}"},
        )
    else:
        return {"message": "Dataset not found"}


@app.get("/evaluate/")
async def ranking(
    gen_id: str = "",
    llm_endpoint: str = "",
    wandb_log: bool = False,
):
    output_file = os.path.join(output_directory, f"{gen_id}.txt")
    if os.path.exists(output_file):
        # write code to rank the questions based on endpoint response for each question in the json file
        qa_data = read_qa_data(output_file)
        endpoint_configs = read_endpoint_configurations(llm_endpoint)
        await evaluate_qa_data(qa_data, endpoint_configs, wandb_log)
        return JSONResponse(
            content={
                "message": "Ranker is complete, Use the /report/gen_id endpoint to download ranked reports for each question",
                "gen_id": gen_id,
            }
        )
    else:
        return {"message": "Dataset with id {gen_id} not found"}


@app.get("/report/{gen_id}")
async def download(gen_id: str):
    """
    Downloads a dataset with the given `gen_id` and returns a FileResponse object if the dataset exists.
    If the dataset does not exist, returns a dictionary with a "message" key and a corresponding error message.
    """
    output_file = os.path.join(output_directory, f"ranked_{gen_id}.txt")
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
