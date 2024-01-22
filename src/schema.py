# schema.py

from pydantic import BaseModel
from typing import List


class DatasetBase(BaseModel):
    name: str
    userid: int
    orgid: int
    type: str
    chat_type: str
    sample_size: int
    number_of_questions: int
    reference_chunk: str
    reference_chunk_max_distance: int
    chunk_size: int

    class Config:
        orm_mode = True


class QADataBase(BaseModel):
    dataset_id: int
    ts: str
    score: float

    class Config:
        orm_mode = True


class LLMEndpointBase(BaseModel):
    name: str
    endpoint_url: str

    class Config:
        orm_mode = True


class EvaluationBase(BaseModel):
    dataset_id: int
    llm_endpoint_id: int
    qa_data_id: int
    ts: str
    score: float

    class Config:
        orm_mode = True
