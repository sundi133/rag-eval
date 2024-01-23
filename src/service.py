import os
import uuid
import asyncio
import logging
import json
import os, sys
import requests

from dotenv import load_dotenv
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ValidationError
from fastapi.encoders import jsonable_encoder
from fastapi import status
from sqlalchemy import select, desc, join, and_
from fastapi import (
    FastAPI,
    File,
    Form,
    UploadFile,
    WebSocket,
    HTTPException,
    Depends,
    Query,
    Request,
    Depends,
)
from sqlalchemy.orm import Session
from sqlalchemy import select, create_engine, desc, func
from fastapi.responses import JSONResponse
from fastapi.responses import FileResponse
from fastapi import BackgroundTasks
from fastapi_sqlalchemy import DBSessionMiddleware, db
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from databases import Database
from datetime import datetime

from .models import (
    Base,
    Dataset,
    QAData,
    LLMEndpoint,
    EvaluationProfiles,
    Assessments,
    EvaluationRuns,
    ApiToken,
)
from .responses import (
    DatasetResponse,
    QADataResponse,
    LLMEndpointResponse,
    AssessmentResponse,
    EvaluationChatResponse,
    EvaluationProfileResponse,
    AssessmentResponseWithRunId,
    ApiTokenResponse,
    EvaluationRunResponse,
)
from .ranking import evaluate_qa_data
from .generator import qa_generator_task
from .simulation import simulation_task
from .evaluation import evaluation_task
from .utils import (
    read_qa_data,
    read_endpoint_configurations,
    score_answer,
    get_llm_answer,
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
ch = logging.StreamHandler()
ch.setFormatter(formatter)
logger.addHandler(ch)

app = FastAPI()
cwd = "/tmp"
upload_directory = os.path.join(cwd, "qa_generator_uploads")
output_directory = os.path.join(cwd, "qa_generator_outputs")

if not os.path.exists(upload_directory):
    os.makedirs(upload_directory)
if not os.path.exists(output_directory):
    os.makedirs(output_directory)


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

load_dotenv(os.path.join(BASE_DIR, ".env"))
sys.path.append(BASE_DIR)

app.add_middleware(DBSessionMiddleware, db_url=os.environ["POSTGRES_URL"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

POSTGRES_URL = os.environ["POSTGRES_URL"]
database = Database(POSTGRES_URL)
engine = create_engine(POSTGRES_URL, pool_pre_ping=True)
Base.metadata.create_all(bind=engine)


def get_db():
    db = Session(autocommit=False, bind=engine)
    try:
        yield db
    finally:
        db.close()


def get_user_info(user_id: str, token: str = None) -> (bool, str, str):
    if token is not None and token != "":
        # Query the database for the token
        query = (
            select(ApiToken).filter(ApiToken.token == token).order_by(desc(ApiToken.ts))
        )
        # db = Depends(get_db)
        token_row = db.session.execute(query).scalars().first()

        # Check if token is found and valid
        if token_row is None:
            return (False, None, None)

        # Extract userId and orgId from the token row
        userId = token_row.userid
        orgId = token_row.orgid

        return (True, userId, orgId)

    if user_id is None or user_id == "":
        return (False, None, None)

    bearer_token = os.environ["CLERK_SECRET_KEY"]
    authorization = f"Bearer {bearer_token}"
    headers = {"Authorization": authorization}
    url = f"https://api.clerk.com/v1/users/{user_id}"
    response = requests.get(url, headers=headers)

    return (response.status_code == 200, user_id, None)


@app.get("/api")
def root():
    return {"status": "ok"}


@app.get("/api/health")
def health():
    return {"status": "pong"}


@app.post("/api/generate")
async def generator(
    background_tasks: BackgroundTasks,
    name: str = Form(default=""),
    userId: str = Form(default=""),
    orgId: str = Form(default=""),
    dataset_type: str = Form(default=""),
    chunk_size: int = Form(default=2000, ge=1, le=8000),
    persona: str = Form(default=""),
    behavior: str = Form(default=""),
    demographic: str = Form(default=""),
    sentiment: str = Form(default=""),
    error_type: str = Form(default="normal"),
    resident_type: str = Form(default=""),
    family_status: str = Form(default=""),
    follow_up_depth: int = Form(default=3, ge=1, le=10),
    tags: str = Form(default=""),
    data_path: str = Form(default="", max_length=1000, min_length=0),
    number_of_questions: int = Form(default=5, ge=1, le=10000),
    sample_size: int = Form(default=5, ge=1, le=100),
    products_group_size: int = Form(default=1, ge=1, le=1000),
    group_columns: str = Form(default=""),  # ex - brand,category,gender
    model_name: str = Form(default="gpt-3.5-turbo"),
    prompt_key: str = Form(default="prompt_key_readme"),
    llm_type: str = Form(default=".txt"),
    generator_type: str = Form(default="text"),
    metadata: str = Form(default=""),
    crawl_depth: int = Form(default=0, ge=1, le=10),
    max_crawl_links: int = Form(default=0, ge=1, le=1000),
    data_source: str = Form(default="unspecified"),
    openai_api_key: Optional[str] = Form(default=None),
    files: List[UploadFile] = File(default=[]),
    token: str = Form(default=""),
):
    validUser, user, org = get_user_info(userId, token)
    logger.info(f"Valid user: {validUser} {org} {orgId} {token}")
    if not validUser:
        return {"message": "Unauthorized"}
    orgId = orgId if orgId != "" and orgId is not None else org
    userId = userId if userId != "" and userId is not None else user

    data_paths = []
    if files and len(files) > 0:
        for i, file in enumerate(files):
            with open(os.path.join(upload_directory, file.filename), "wb") as f:
                file_content = await file.read()
                f.write(file_content)
            data_paths.append(os.path.join(upload_directory, file.filename))
        if data_path != "":
            # Set data_path to the path of the first file if data_path is empty
            data_paths = data_path.split(",")

    else:
        if data_path == "":
            return {"message": "No file or html web link provided as data source"}
        data_paths = data_path.split(",")

    if llm_type == ".ner":
        generator_type = "ner"
        metadata = data_paths[0]

    qa_type = (
        "_".join(prompt_key.split("_")[3:])
        if len(prompt_key.split("_")) >= 3
        else "simple"
    )
    if openai_api_key is None:
        return {"message": "No OpenAI API key provided"}

    logger.info(f"Data path: {data_path}")
    logger.info(f"Data paths: {data_paths}")
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
    logger.info(f"Dataset type: {dataset_type}")
    logger.info(f"Chunk size: {chunk_size}")
    logger.info(f"qa_type: {qa_type}")
    logger.info(f"user & org: {userId} {orgId}")

    gen_id = uuid.uuid4().hex
    output_file = os.path.join(output_directory, f"{gen_id}.json")
    logger.info(f"Output file: {output_file}")
    grouped_columns = []
    if group_columns:
        for column in group_columns.split(","):
            grouped_columns.append(column)

    try:
        # Create a new Dataset instance
        dataset = Dataset(
            name=name,
            gen_id=gen_id,
            sample_size=sample_size,
            number_of_questions=number_of_questions,
            orgid=orgId,
            userid=userId,
            dataset_type=dataset_type,
            model_name=model_name,
            chunk_size=chunk_size,
            persona=persona,
            behavior=behavior,
            demographic=demographic,
            sentiment=sentiment,
            error_type=error_type,
            resident_type=resident_type,
            family_status=family_status,
            qa_type=qa_type,
            crawl_depth=crawl_depth,
            max_crawl_links=max_crawl_links,
            status="in_progress",
            data_source=data_source,
            tags=tags,
        )

        # Add the instance to the session and flush to generate the ID
        db.session.add(dataset)
        db.session.flush()

        # Now you can access the ID
        dataset_id = dataset.id

        # Commit the changes to the database
        db.session.commit()

        background_tasks.add_task(
            qa_generator_task,
            data_paths,
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
            dataset_id,
            orgId,
            userId,
            persona=persona,
            behavior=behavior,
            demographic=demographic,
            sentiment=sentiment,
            error_type=error_type,
            follow_up_depth=follow_up_depth,
            resident_type=resident_type,
            family_status=family_status,
            chunk_size=chunk_size,
            max_crawl_links=max_crawl_links,
            openai_api_key=openai_api_key,
        )

        return JSONResponse(
            content={
                "message": "Generator in progress, Use the /download/ endpoint to check the status of the generator",
                "gen_id": gen_id,
                "dataset_id": dataset_id,
            }
        )
    except SQLAlchemyError as e:
        # Handle the exception (e.g., log the error, rollback the session)
        db.session.rollback()
        logger.info({"error": f"Error during dataset insertion: {e}"})
        return JSONResponse(
            content={
                "message": "Oops! Something went wrong. Please try again.",
                "gen_id": -1,
            }
        )


@app.get("/api/dataset/search", response_model=List[DatasetResponse])
async def get_dataset(
    search: str,
    org_id: str = Query("", max_length=1000, min_length=0),
    db: Session = Depends(get_db),
):
    query = (
        select(Dataset)
        .filter(
            Dataset.orgid == org_id,
            Dataset.name.ilike(f"%{search}%"),  # Use ilike for case-insensitive search
        )
        .order_by(desc(Dataset.ts))
    )  # Add order_by clause to sort by ts in descending order

    results = db.execute(query).scalars().all()
    return results


@app.get("/api/dataset/list", response_model=List[DatasetResponse])
async def get_dataset(
    org_id: str = Query("", max_length=1000, min_length=0),
    user_id: str = Query("", max_length=1000, min_length=0),
    token: str = Query("", max_length=1000, min_length=0),
    db: Session = Depends(get_db),
):
    validUser, userId, orgId = get_user_info(user_id, token)
    org_id = org_id if org_id != "" and org_id is not None else orgId
    logger.info(f"Valid user: {validUser} {orgId} {org_id}")
    if not validUser:
        return {"message": "Unauthorized"}
    query = select(Dataset).filter(Dataset.orgid == org_id).order_by(desc(Dataset.ts))
    results = db.execute(query).scalars().all()
    return results


@app.get("/api/dataset", response_model=DatasetResponse)
async def get_dataset(
    dataset_id: int,
    org_id: str = Query("", max_length=1000, min_length=0),
    token: str = Query("", max_length=1000, min_length=0),
    db: Session = Depends(get_db),
):
    if org_id is None:
        validUser, userId, orgId = get_user_info(None, token)
        if not validUser:
            return {"message": "Unauthorized"}
        org_id = org_id if org_id != "" and org_id is not None else orgId
    query = select(Dataset).filter(Dataset.id == dataset_id, Dataset.orgid == org_id)
    results = db.execute(query).scalars().first()
    return results


@app.get("/api/dataset/{gen_id}")
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


@app.get("/api/llm-endpoints/list", response_model=List[LLMEndpointResponse])
async def get_llm_endpoints(
    org_id: str = Query("", max_length=1000, min_length=0),
    db: Session = Depends(get_db),
):
    query = (
        select(LLMEndpoint)
        .filter(LLMEndpoint.orgid == org_id)
        .order_by(desc(LLMEndpoint.ts))
    )
    results = db.execute(query).scalars().all()
    return results


@app.get("/api/llm-endpoint", response_model=LLMEndpointResponse)
async def get_endpoint(
    llm_endpoint_id: int,
    org_id: str = Query("", max_length=1000, min_length=0),
    db: Session = Depends(get_db),
):
    query = select(LLMEndpoint).filter(
        LLMEndpoint.id == llm_endpoint_id, LLMEndpoint.orgid == org_id
    )
    results = db.execute(query).scalars().first()
    return results


@app.delete("/api/llm-endpoint")
async def delete_endpoint(
    llm_endpoint_id: int,
    org_id: str = Query("", max_length=1000, min_length=0),
    db: Session = Depends(get_db),
):
    query = select(LLMEndpoint).filter(
        LLMEndpoint.id == llm_endpoint_id, LLMEndpoint.orgid == org_id
    )
    results = db.execute(query).scalars().first()
    if results:
        db.delete(results)
        db.commit()
        return {"message": "Endpoint deleted successfully"}
    else:
        return {"message": "Endpoint not found"}


@app.post("/api/endpoint/add")
async def generator(
    name: str = Form(default=""),
    endpoint_url: str = Form(default=""),
    userId: str = Form(default="-1"),
    orgId: str = Form(default="-1"),
    access_token: str = Form(default=""),
    payload_format: str = Form(default=""),
    payload_user_key: str = Form(default=""),
    payload_message_key: str = Form(default=""),
    payload_response_key: str = Form(default=""),
    http_method: str = Form(default=""),
    requests_per_minute: int = Form(default=10, ge=1, le=100),
):
    if name == "":
        return {"message": "No name provided for endpoint"}
    if endpoint_url == "":
        return {"message": "No endpoint url provided for endpoint"}
    if get_user_info(userId) == False:
        return {"message": "Unauthorized"}
    try:
        # Create a new LLMEndpoint instance
        endpoint = LLMEndpoint(
            name=name,
            endpoint_url=endpoint_url,
            orgid=orgId,
            userid=userId,
            access_token=access_token,
            payload_format=payload_format,
            payload_user_key=payload_user_key,
            payload_response_key=payload_response_key,
            payload_message_key=payload_message_key,
            http_method=http_method,
            requests_per_minute=requests_per_minute,
        )

        # Add the instance to the session and flush to generate the ID
        db.session.add(endpoint)
        db.session.flush()

        # Now you can access the ID
        endpoint_id = endpoint.id

        # Commit the changes to the database
        db.session.commit()

        return JSONResponse(
            content={
                "message": "Endpoint added successfully",
                "endpoint_id": endpoint_id,
            }
        )
    except SQLAlchemyError as e:
        # Handle the exception (e.g., log the error, rollback the session)
        db.session.rollback()
        logger.info({"error": f"Error during endpoint insertion: {e}"})
        return JSONResponse(
            content={
                "message": "Oops! Something went wrong. Please try again.",
                "endpoint_id": -1,
            }
        )


@app.get("/api/qa-data", response_model=List[QADataResponse])
async def get_qa_data(
    dataset_id: int,
    org_id: str = Query("", max_length=1000, min_length=0),
    token: str = Query("", max_length=1000, min_length=0),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1),
    db: Session = Depends(get_db),
):
    if org_id == "" or org_id is None:
        validUser, userId, orgId = get_user_info(None, token)
        if not validUser:
            return {"message": "Unauthorized"}
        org_id = org_id if org_id != "" and org_id is not None else orgId
        logger.info(f"Valid user: {validUser} {orgId} {org_id}")
    query = (
        select(QAData)
        .filter(QAData.dataset_id == dataset_id, QAData.orgid == org_id)
        .offset(skip)
        .limit(limit)
    )
    results = db.execute(query).scalars().all()
    return results


@app.post("/api/simulation/add")
async def add_simulation(
    background_tasks: BackgroundTasks,
    user_id: str = Form(default=""),
    org_id: str = Form(default=""),
    token: str = Form(default=""),
    start_simulation: bool = Form(default=True),
    name: str = Form(default=""),
    endpoint_url_id: int = Form(default=""),
    dataset_id: int = Form(default=""),
    num_users: int = Form(default=1, ge=1, le=100),
    percentage_of_questions: int = Form(default=0, ge=1, le=100),
    order_of_questions: str = Form(default=""),
):
    validUser, userId, orgId = get_user_info(user_id, token)

    user_id = user_id if user_id != "" and user_id is not None else userId
    org_id = org_id if org_id != "" and org_id is not None else orgId

    if validUser == False:
        return {"message": "Unauthorized"}
    try:
        if endpoint_url_id == "":
            # Create a new Dataset instance
            simulation = EvaluationProfiles(
                name=name,
                userid=user_id,
                orgid=org_id,
                dataset_id=dataset_id,
                num_users=num_users,
                percentage_of_questions=percentage_of_questions,
                order_of_questions=order_of_questions,
                simulation_id=f"{uuid.uuid4().hex.upper()[0:12]}",
            )
        else:
            # Create a new Dataset instance
            simulation = EvaluationProfiles(
                name=name,
                userid=user_id,
                orgid=org_id,
                endpoint_url_id=endpoint_url_id,
                dataset_id=dataset_id,
                num_users=num_users,
                percentage_of_questions=percentage_of_questions,
                order_of_questions=order_of_questions,
                simulation_id=f"{uuid.uuid4().hex.upper()[0:12]}",
            )

        # Add the instance to the session and flush to generate the ID
        db.session.add(simulation)
        db.session.flush()

        # Now you can access the ID
        simulation_id = simulation.id

        # Commit the changes to the database
        db.session.commit()

        if start_simulation:
            simulation_run = EvaluationRuns(
                orgid=org_id,
                evaluation_profile_id=simulation_id,
                ts=datetime.utcnow(),
                score=0.0,
            )
            db.session.add(simulation_run)
            db.session.flush()

            simulation_run_id = simulation_run.id

            # Commit the changes to the database
            db.session.commit()

            background_tasks.add_task(
                simulation_task,
                simulation_id,
                simulation_run_id,
                user_id,
                org_id,
                endpoint_url_id,
                dataset_id,
                num_users,
                percentage_of_questions,
                order_of_questions,
            )
        return JSONResponse(
            content={
                "message": "Evaluation added successfully",
                "evaluation_profile_id": simulation_id,
            }
        )
    except SQLAlchemyError as e:
        # Handle the exception (e.g., log the error, rollback the session)
        db.session.rollback()
        logger.info({"error": f"Error during simulation insertion: {e}"})
        return JSONResponse(
            content={
                "message": "Oops! Something went wrong. Please try again.",
                "evaluation_profile_id": None,
            }
        )


@app.post("/api/simulation/trigger")
async def trigger_simulation(
    background_tasks: BackgroundTasks,
    user_id: str = Form(default="", max_length=1000, min_length=0),
    org_id: str = Form(default="", max_length=1000, min_length=0),
    simulation_id: str = Form(default="", max_length=1000, min_length=0),
    db_session: Session = Depends(get_db),
):
    validUser, userId, orgId = get_user_info(user_id, None)

    if validUser == False:
        return {"message": "Unauthorized"}

    query = select(EvaluationProfiles).filter(
        EvaluationProfiles.id == int(simulation_id), EvaluationProfiles.orgid == org_id
    )

    logger.info(
        {
            "message": "Triggering simulation",
            "simulation_id": int(simulation_id),
        }
    )
    result = db_session.execute(query).scalars().first()

    if result:
        # Update the status
        result.status = "in_progress"
        # Commit the changes to the database
        db_session.commit()
    else:
        logger.info("SimulationProfile not found")

    simulation_run = EvaluationRuns(
        orgid=org_id,
        evaluation_profile_id=result.id,
        ts=datetime.utcnow(),
        score=0.0,
        run_status="in_progress",
    )

    # Add the instance to the session and flush to generate the ID
    db.session.add(simulation_run)
    db.session.flush()

    # Now you can access the ID
    simulation_run_id = simulation_run.id

    # Commit the changes to the database
    db.session.commit()

    background_tasks.add_task(
        simulation_task,
        result.id,
        simulation_run_id,
        user_id,
        org_id,
        result.endpoint_url_id,
        result.dataset_id,
        result.num_users,
        result.percentage_of_questions,
        result.order_of_questions,
    )
    return JSONResponse(
        content={
            "message": "Evaluation added successfully",
            "simulation_id": simulation_id,
        }
    )


@app.get("/api/simulation/list", response_model=List[EvaluationProfileResponse])
async def get_endpoint_list(
    user_id: str = Query("", max_length=1000, min_length=0),
    org_id: str = Query("", max_length=1000, min_length=0),
    token: str = Query("", max_length=1000, min_length=0),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1),
    db: Session = Depends(get_db),
):
    validUser, userId, orgId = get_user_info(user_id, token)

    if validUser == False:
        return {"message": "Unauthorized"}

    org_id = org_id if org_id != "" and org_id is not None else orgId

    query = (
        select(EvaluationProfiles)
        .filter(EvaluationProfiles.orgid == org_id)
        .offset(skip)
        .limit(limit)
    ).order_by(desc(EvaluationProfiles.ts))

    results = db.execute(query).scalars().all()
    return results


@app.get("/api/simulation/id", response_model=EvaluationProfileResponse)
async def get_endpoint_id(
    simulation_id: int,
    org_id: str = Query("", max_length=1000, min_length=0),
    db: Session = Depends(get_db),
):
    query = select(EvaluationProfiles).filter(
        EvaluationProfiles.id == simulation_id, EvaluationProfiles.orgid == org_id
    )
    results = db.execute(query).scalars().first()
    return results


@app.post("/api/evaluation/start-assesement")
async def qa_start_assesement(
    evaluation_id: int = Form(default=None, ge=0),
    org_id: str = Form(default="", max_length=1000, min_length=0),
    user_id: str = Form(default="", max_length=1000, min_length=0),
    token: str = Form(default="", max_length=1000, min_length=0),
):
    validUser, userId, orgId = get_user_info(user_id, token)
    user_id = user_id if user_id != "" and user_id is not None else userId
    org_id = org_id if org_id != "" and org_id is not None else orgId

    if validUser == False:
        return {"message": "Unauthorized"}

    query = select(EvaluationProfiles).filter(
        EvaluationProfiles.id == evaluation_id, EvaluationProfiles.orgid == org_id
    )
    result = db.session.execute(query).scalars().first()
    if result:
        # Update the status
        result.status = "in_progress"
        # Commit the changes to the database
        db.session.commit()
    else:
        logger.info("SimulationProfile not found")

    evaluation_id = f"{uuid.uuid4().hex.upper()[0:32]}"
    simulation_run = EvaluationRuns(
        orgid=org_id,
        evaluation_profile_id=result.id,
        ts=datetime.utcnow(),
        score=0.0,
        run_status="in_progress",
        evaluation_id=evaluation_id,
    )

    # Add the instance to the session and flush to generate the ID
    db.session.add(simulation_run)
    db.session.flush()

    # Now you can access the ID
    simulation_run_id = simulation_run.id

    # Commit the changes to the database
    db.session.commit()

    return JSONResponse(
        content={
            "message": "Evaluation run in progress",
            "evaluation_run_id": simulation_run_id,
        }
    )


@app.post("/api/evaluation/end-assesement")
async def qa_end_assesement(
    evaluation_run_id: int =  Form(default=None, ge=0),
    org_id: str = Form(default="", max_length=1000, min_length=0),
    user_id: str = Form(default="", max_length=1000, min_length=0),
    token: str = Form(default="", max_length=1000, min_length=0),
):
    validUser, userId, orgId = get_user_info(user_id, token)
    user_id = user_id if user_id != "" and user_id is not None else userId
    org_id = org_id if org_id != "" and org_id is not None else orgId

    if validUser == False:
        return {"message": "Unauthorized"}

    query = select(EvaluationRuns).filter(
        EvaluationRuns.id == evaluation_run_id, EvaluationRuns.orgid == org_id
    )
    result = db.session.execute(query).scalars().first()
    evaluation_profile_id = result.evaluation_profile_id
    if result:
        # Update the status
        result.run_status = "completed"
        # Commit the changes to the database
        db.session.commit()
    else:
        logger.info("SimulationRuns not found")

    query = select(EvaluationProfiles).filter(
        EvaluationProfiles.id == evaluation_profile_id, EvaluationProfiles.orgid == org_id
    )
    result = db.session.execute(query).scalars().first()
    if result:
        # Update the status
        result.status = "completed"
        # Commit the changes to the database
        db.session.commit()
    
    return JSONResponse(
        content={
            "message": "Evaluation run is completed",
            "evaluation_run_id": evaluation_run_id,
        }
    )


@app.post("/api/evaluation/qadata-access")
async def qa_data_evaulate(
    background_tasks: BackgroundTasks,
    evaluation_run_id: int = Form(default=None, ge=0),
    chat_id: int = Form(default=None, ge=0),
    org_id: str = Form(default="", max_length=1000, min_length=0),
    user_id: str = Form(default="", max_length=1000, min_length=0),
    token: str = Form(default="", max_length=1000, min_length=0),
    question: str = Form(default="", min_length=0),
    verified_answer: str = Form(default="", min_length=0),
    verified_reference_context: str = Form(default="", min_length=0),
    app_generated_answer: str = Form(default="", min_length=0),
    app_generated_context: List[str] = Form(default=[""]),
    model_name: str = Form(default="gpt-3.5-turbo", min_length=0),
    evaluation_user_prompt: str = Form(default="", min_length=0),
    openai_api_key: Optional[str] = Form(default=None),
    db: Session = Depends(get_db),
):
    validUser, userId, orgId = get_user_info(user_id, token)
    user_id = user_id if user_id != "" and user_id is not None else userId
    org_id = org_id if org_id != "" and org_id is not None else orgId
    if not validUser:
        return {"message": "Unauthorized"}
    try:
        query = select(EvaluationRuns).filter(
            EvaluationRuns.id == int(evaluation_run_id), EvaluationRuns.orgid == org_id
        )

        result = db.execute(query).scalars().first()

        simulation_run_id = result.id
        evaluation_profile_id = result.evaluation_profile_id
        evaluation_id = result.evaluation_id

        simulation_profile = select(EvaluationProfiles).filter(
            EvaluationProfiles.id == evaluation_profile_id, EvaluationProfiles.orgid == org_id
        )

        simulation_result = db.execute(simulation_profile).scalars().first()

        dataset_id = simulation_result.dataset_id

        logger.info(
            {
                "message": "Triggering simulation",
                "simulation_id": evaluation_run_id,
                "model_name": model_name,
                "evaluation_id": evaluation_id,
                "dataset_id": dataset_id,
                "simulation_run_id": simulation_run_id,
                "chat_id": chat_id,
                evaluation_id: evaluation_id,
            }
        )

        background_tasks.add_task(
            evaluation_task,
            dataset_id,
            evaluation_id,
            chat_id,
            org_id,
            user_id,
            question,
            verified_answer,
            verified_reference_context,
            app_generated_answer,
            app_generated_context,
            model_name,
            evaluation_user_prompt,
            evaluation_profile_id,
            simulation_run_id,
            openai_api_key,
        )

        # Add the instance to the session and flush to generate the ID
        return JSONResponse(
            content={
                "message": "Assesement added successfully",
                "evaluation_run_id": evaluation_run_id,
            }
        )
    except SQLAlchemyError as e:
        logger.info({"error": f"Error during evaluation insertion: {e}"})
        return JSONResponse(
            content={
                "message": "Oops! Something went wrong. Please try again.",
                "evaluation_run_id": evaluation_run_id,
            }
        )


@app.get("/api/assesements/list", response_model=List[EvaluationRunResponse])
async def get_assesements_list(
    user_id: str = Query("", max_length=1000, min_length=0),
    org_id: str = Query("", max_length=1000, min_length=0),
    token: str = Query("", max_length=1000, min_length=0),
    db: Session = Depends(get_db),
):
    validUser, userId, orgId = get_user_info(user_id, token)
    org_id = org_id if org_id != "" and org_id is not None else orgId

    if validUser == False:
        return {"message": "Unauthorized"}

    org_id = org_id if org_id != "" and org_id is not None else orgId

    query = (
        select(EvaluationRuns)
        .filter(EvaluationRuns.orgid == org_id)
        .order_by(desc(EvaluationRuns.ts))
    )

    results = db.execute(query).scalars().all()
    return results


@app.get("/api/evaluation/list", response_model=List[AssessmentResponse])
async def get_evaluation_list(
    user_id: str = Query("", max_length=1000, min_length=0),
    org_id: str = Query("", max_length=1000, min_length=0),
    db: Session = Depends(get_db),
):
    validUser, userId, orgId = get_user_info(user_id, None)

    if validUser == False:
        return {"message": "Unauthorized"}

    query = (
        select(
            [
                Assessments.evaluation_profile_id.label("evaluation_profile_id"),
                func.avg(Assessments.score).label("average_score"),
                func.max(Assessments.ts).label("last_updated"),
                func.count(Assessments.id).label("number_of_evaluations"),
                func.count(func.distinct(Assessments.simulation_userid)).label(
                    "distinct_users"
                ),
                Dataset.name.label("dataset_name"),
                EvaluationProfiles.name.label("simulation_name"),
                EvaluationProfiles.status.label("status"),
            ]
        )
        .join(Dataset, Assessments.dataset_id == Dataset.id)
        .join(EvaluationProfiles, Assessments.evaluation_profile_id == EvaluationProfiles.id)
        .where(Assessments.orgid == org_id)
        .group_by(
            Assessments.evaluation_profile_id,
            Dataset.name,
            EvaluationProfiles.name,
            EvaluationProfiles.status,
        )
        .order_by(desc("last_updated"))
    )

    results = db.execute(query).all()
    return results


@app.get(
    "/api/evaluation/id", response_model=List[AssessmentResponseWithRunId]
)
async def get_evaluation_id(
    user_id: str = Query("", max_length=1000, min_length=0),
    org_id: str = Query("", max_length=1000, min_length=0),
    token: str = Query("", max_length=1000, min_length=0),
    evaluation_profile_id: int = Query(None, ge=0),
    db: Session = Depends(get_db),
):
    validUser, userId, orgId = get_user_info(user_id, token)
    user_id = user_id if user_id != "" and user_id is not None else userId
    org_id = org_id if org_id != "" and org_id is not None else orgId

    if validUser == False:
        return {"message": "Unauthorized"}

    
    query = (
        select(
            [
                Assessments.evaluation_profile_id.label("evaluation_profile_id"),
                Assessments.run_id.label("run_id"),
                Assessments.evaluation_id.label("evaluation_id"),
                func.avg(Assessments.score).label("average_score"),
                func.avg(Assessments.min_retrieval_score).label("min_retrieval_score"),
                func.avg(Assessments.max_retrieval_score).label("max_retrieval_score"),
                func.max(Assessments.ts).label("last_updated"),
                func.count(Assessments.id).label("number_of_evaluations"),
                func.count(func.distinct(Assessments.simulation_userid)).label("distinct_users"),
                Dataset.name.label("dataset_name"),
                EvaluationProfiles.name.label("simulation_name"),
                EvaluationProfiles.status.label("status"),
            ]
        )
        .join(EvaluationProfiles, EvaluationProfiles.id == Assessments.evaluation_profile_id)  # Adjusted join
        .join(Dataset, Dataset.id == Assessments.dataset_id)  # Adjusted join
        .join(EvaluationRuns, EvaluationRuns.id == Assessments.run_id)  # Adjusted join
        .where(
            (EvaluationProfiles.orgid == org_id) & 
            (EvaluationProfiles.id == evaluation_profile_id)
            # (Assessments.min_retrieval_score != None) &
            # (Assessments.max_retrieval_score != None)
        )
        .group_by(
            Assessments.evaluation_profile_id,
            Assessments.run_id,
            Assessments.evaluation_id,
            Dataset.name,
            EvaluationProfiles.name,
            EvaluationProfiles.status,
        )
        .order_by(desc("last_updated"))
    )

    results = db.execute(query).all()
    logger.info(results)
    return results


@app.get("/api/evaluation/chat", response_model=List[EvaluationChatResponse])
async def evaluation(
    user_id: str = Query("", max_length=1000, min_length=0),
    org_id: str = Query("", max_length=1000, min_length=0),
    token: str = Query("", max_length=1000, min_length=0),
    filter_score: float = Query(0.0, ge=0.0, le=1.0),
    run_id: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    validUser, userId, orgId = get_user_info(user_id, token)
    user_id = user_id if user_id != "" and user_id is not None else userId
    org_id = org_id if org_id != "" and org_id is not None else orgId

    if validUser == False:
        return {"message": "Unauthorized"}

    query = (
        select(
            [
                QAData.chat_messages.label("chat_messages"),
                QAData.ts.label("timestamp"),
                QAData.reference_chunk.label("reference_chunk"),
                Assessments.run_id.label("run_id"),
                Assessments.score.label("score"),
                Assessments.score_reason.label("score_reason"),
                Assessments.endpoint_response.label("endpoint_response"),
                Assessments.min_retrieval_score.label("min_retrieval_score"),
                Assessments.max_retrieval_score.label("max_retrieval_score"),
                Assessments.avg_retrieval_score.label("avg_retrieval_score"),
                Assessments.verified_reference_context.label("verified_reference_context"),
                Assessments.chunks_retrieved.label("chunks_retrieved"),
            ]
        )
        .join(Assessments, QAData.id == Assessments.qa_data_id)
        .where(Assessments.score >= filter_score)
        .filter(
            and_(
                Assessments.orgid == org_id,
                Assessments.run_id == run_id,
            )
        )
        .order_by(desc(QAData.ts))
    )

    results = db.execute(query).all()  # scalars() returns a list of tuples
    return results


@app.get("/api/tokens", response_model=List[ApiTokenResponse])
async def get_tokens(
    user_id: str = Query("", max_length=1000, min_length=0),
    org_id: str = Query("", max_length=1000, min_length=0),
    db: Session = Depends(get_db),
):
    validUser, userId, orgId = get_user_info(user_id, None)

    if validUser == False:
        return {"message": "Unauthorized"}

    query = (
        select(ApiToken)
        .filter(ApiToken.userid == user_id, ApiToken.orgid == org_id)
        .order_by(desc(ApiToken.ts))
    )

    results = db.execute(query).scalars().all()
    return results


@app.post("/api/token/add")
async def add_token(
    user_id: str = Form(default=""),
    org_id: str = Form(default=""),
    name: str = Form(default=""),
):
    validUser, userId, orgId = get_user_info(user_id, None)

    if validUser == False:
        return {"message": "Unauthorized"}

    try:
        # Create a new Dataset instance
        token = ApiToken(
            userid=user_id,
            orgid=org_id,
            token=uuid.uuid4().hex,
            name=name,
        )

        # Add the instance to the session and flush to generate the ID
        db.session.add(token)
        db.session.flush()

        # Now you can access the ID
        token_id = token.id

        # Commit the changes to the database
        db.session.commit()

        return JSONResponse(
            content={
                "message": "Token added successfully",
                "token_id": token_id,
            }
        )
    except SQLAlchemyError as e:
        # Handle the exception (e.g., log the error, rollback the session)
        db.session.rollback()
        logger.info({"error": f"Error during token insertion: {e}"})
        return JSONResponse(
            content={
                "message": "Oops! Something went wrong. Please try again.",
                "token_id": -1,
            }
        )


@app.get("/api/ranking/{gen_id}")
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


@app.websocket("/api/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    for i in range(10):
        await websocket.send_text(f"Streamed message {i}")
        await asyncio.sleep(1)  # Simulate a delay between messages
