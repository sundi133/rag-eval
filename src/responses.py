import os
import uuid
import asyncio
import logging
import json
import os, sys
import requests

from typing import List, Optional
from pydantic import BaseModel, ValidationError

from .models import Base, Dataset, QAData, LLMEndpoint
from datetime import datetime


class ApiTokenResponse(BaseModel):
    id: int
    name: Optional[str]  # Allow name to be None
    token: str
    userid: str
    orgid: str
    ts: datetime


class DatasetResponse(BaseModel):
    id: int
    name: str
    gen_id: str
    sample_size: int
    number_of_questions: int
    orgid: str
    userid: str
    ts: datetime
    dataset_type: Optional[str]  # Allow dataset_type to be None
    model_name: Optional[str]  # Allow model_name to be None
    chunk_size: Optional[int]  # Allow chunk_size to be None
    persona: Optional[str]  # Allow persona to be None
    behavior: Optional[str]  # Allow behavior to be None
    demographic: Optional[str]  # Allow demographic to be None
    sentiment: Optional[str]  # Allow sentiment to be None
    error_type: Optional[str]  # Allow error_type to be None
    resident_type: Optional[str]  # Allow resident_type to be None
    family_status: Optional[str]  # Allow family_status to be None
    qa_type: Optional[str]  # Allow qa_type to be None
    status: Optional[str]  # Allow status to be None
    error_msg: Optional[str]  # Allow error_msg to be None
    data_source: Optional[str]  # Allow data_source to be None
    error_msg: Optional[str]  # Allow error_msg to be None
    tags: Optional[str]  # Allow tags to be None


class QADataResponse(BaseModel):
    id: int
    userid: str
    orgid: str
    dataset_id: int
    ts: datetime
    chat_messages: str
    reference_chunk: str


class LLMEndpointResponse(BaseModel):
    id: int
    userid: str
    orgid: str
    name: str
    endpoint_url: str
    ts: datetime
    access_token: Optional[str]  # Allow access_token to be None
    payload_format: Optional[str]  # Allow payload_format to be None
    payload_user_key: Optional[str]  # Allow payload_user_key to be None
    payload_message_key: Optional[str]  # Allow payload_message_key to be None
    payload_response_key: Optional[str]  # Allow payload_response_key to be None
    http_method: Optional[str]  # Allow http_method to be None
    requests_per_minute: Optional[int]  # Allow requests_per_minute to be None


class EvaluationProfileResponse(BaseModel):
    id: int
    name: Optional[str]
    endpoint_url_id: Optional[int]
    dataset_id: Optional[int]
    num_users: Optional[int]
    percentage_of_questions: Optional[int]
    order_of_questions: Optional[str]
    ts: Optional[datetime]
    status: Optional[str]


class EvaluationRunResponse(BaseModel):
    id: int
    evaluation_profile_id: int
    ts: datetime
    run_status: Optional[str]


class AssessmentResponse(BaseModel):
    evaluation_profile_id: int
    average_score: float
    dataset_name: str
    simulation_name: str
    last_updated: datetime
    number_of_evaluations: int
    distinct_users: Optional[int]  # Allow distinct_users to be None
    status: Optional[str]  # Allow status to be None


class AssessmentResponseWithRunId(BaseModel):
    evaluation_profile_id: int
    run_id: int
    average_score: float
    dataset_name: str
    simulation_name: str
    last_updated: datetime
    evaluation_id: str
    number_of_evaluations: int
    distinct_users: Optional[int]  # Allow distinct_users to be None
    status: Optional[str]  # Allow status to be None
    min_retrieval_score: Optional[float]  # Allow min_retrieval_score to be None
    max_retrieval_score: Optional[float]  # Allow max_retrieval_score to be None


class EvaluationChatResponse(BaseModel):
    chat_messages: str
    timestamp: datetime
    reference_chunk: str
    score: float
    score_reason: Optional[str]  # Allow score_reason to be None
    run_id: Optional[int]  # Allow run_id to be None
    endpoint_response: str
    verified_reference_context: Optional[
        str
    ]  # Allow verified_reference_context to be None
    chunks_retrieved: Optional[List[str]]  # Allow chunks_retrieved to be None
    min_retrieval_score: Optional[float]  # Allow min_retrieval_score to be None
    max_retrieval_score: Optional[float]  # Allow max_retrieval_score to be None
    avg_retrieval_score: Optional[float]  # Allow avg_retrieval_score to be None
