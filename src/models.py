from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

# --- Security Fix: Import cryptography for field encryption ---
try:
    from cryptography.fernet import Fernet, InvalidToken
except ImportError:
    Fernet = None
    InvalidToken = Exception

import os
import base64

Base = declarative_base()

# --- Security Fix: Helper for encryption key management ---
def get_llm_token_encryption_key():
    key = os.environ.get("LLM_TOKEN_ENCRYPTION_KEY")
    if key is None:
        raise RuntimeError("LLM_TOKEN_ENCRYPTION_KEY environment variable not set")
    if isinstance(key, str):
        try:
            key_bytes = key.encode()
            # Validate base64 and length
            decoded = base64.urlsafe_b64decode(key_bytes)
            if len(decoded) != 32:
                raise RuntimeError("LLM_TOKEN_ENCRYPTION_KEY is invalid. Must be 32 url-safe base64-encoded bytes.")
        except Exception:
            raise RuntimeError("LLM_TOKEN_ENCRYPTION_KEY is invalid. Must be 32 url-safe base64-encoded bytes.")
    else:
        key_bytes = key
    if Fernet is None:
        raise RuntimeError("cryptography.fernet is required for token encryption")
    try:
        Fernet(key if isinstance(key, bytes) else key.encode())
    except Exception:
        raise RuntimeError("LLM_TOKEN_ENCRYPTION_KEY is invalid. Must be 32 url-safe base64-encoded bytes.")
    return key if isinstance(key, bytes) else key.encode()

def encrypt_token(token: str) -> str:
    if token is None:
        return None
    if Fernet is None:
        raise RuntimeError("cryptography.fernet is required for token encryption")
    key = get_llm_token_encryption_key()
    f = Fernet(key)
    return f.encrypt(token.encode()).decode()

def decrypt_token(token: str) -> str:
    if token is None:
        return None
    if Fernet is None:
        raise RuntimeError("cryptography.fernet is required for token decryption")
    key = get_llm_token_encryption_key()
    f = Fernet(key)
    try:
        return f.decrypt(token.encode()).decode()
    except Exception:
        # If token is not encrypted, return as is (for backward compatibility)
        return token

class ApiToken(Base):
    __tablename__ = "api_tokens"

    id = Column(Integer, primary_key=True, index=True)
    userid = Column(String)
    orgid = Column(String)
    name = Column(String)
    token = Column(String)
    ts = Column(DateTime, default=datetime.utcnow)

class Dataset(Base):
    __tablename__ = "datasets"

    id = Column(Integer, primary_key=True, index=True)
    gen_id = Column(String, index=True)
    name = Column(String, index=True)
    userid = Column(String)
    orgid = Column(String)
    type = Column(String)
    chat_type = Column(String)
    sample_size = Column(Integer)
    number_of_questions = Column(Integer)
    chunk_size = Column(Integer)
    reference_chunk_max_distance = Column(Integer)
    ts = Column(DateTime, default=datetime.utcnow)
    dataset_type = Column(String)
    model_name = Column(String)
    persona = Column(String)
    behavior = Column(String)
    demographic = Column(String)
    sentiment = Column(String)
    error_type = Column(String)
    follow_up_depth = Column(Integer)
    resident_type = Column(String)
    family_status = Column(String)
    qa_type = Column(String)
    crawl_depth = Column(Integer)
    max_crawl_links = Column(Integer)
    status = Column(String)
    error_msg = Column(String)
    data_source = Column(String)
    tags = Column(String)
    tokens_cost = Column(Float, nullable=True)
    tokens_used = Column(Integer, nullable=True)

    # Define relationships
    qa_data = relationship("QAData", back_populates="dataset")
    assessments = relationship("Assessments", back_populates="dataset")
    evaluation_profiles = relationship("EvaluationProfiles", back_populates="dataset")

class QAData(Base):
    __tablename__ = "qa_data"

    id = Column(Integer, primary_key=True, index=True)
    userid = Column(String)
    orgid = Column(String)
    dataset_id = Column(Integer, ForeignKey("datasets.id"))
    ts = Column(DateTime, default=datetime.utcnow)
    chat_messages = Column(JSON)
    reference_chunk = Column(String)

    # Define relationships
    dataset = relationship("Dataset", back_populates="qa_data")
    assessments = relationship("Assessments", back_populates="qa_data")

class LLMEndpoint(Base):
    __tablename__ = "llm_endpoints"

    id = Column(Integer, primary_key=True, index=True)
    userid = Column(String)
    orgid = Column(String)
    name = Column(String, index=True)
    endpoint_url = Column(String)
    ts = Column(DateTime, default=datetime.utcnow)
    _access_token = Column("access_token", String)
    payload_format = Column(String)
    payload_user_key = Column(String)
    payload_message_key = Column(String)
    payload_response_key = Column(String)
    http_method = Column(String)
    requests_per_minute = Column(Integer)

    assessments = relationship("Assessments", back_populates="llm_endpoint")
    evaluation_profiles = relationship(
        "EvaluationProfiles", back_populates="llm_endpoint"
    )

    @property
    def access_token(self):
        if self._access_token is None:
            return None
        return decrypt_token(self._access_token)

    @access_token.setter
    def access_token(self, value):
        if value is None:
            self._access_token = None
        else:
            self._access_token = encrypt_token(value)

class EvaluationProfiles(Base):
    __tablename__ = "evaluation_profiles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    userid = Column(String)
    orgid = Column(String)
    endpoint_url_id = Column(Integer, ForeignKey("llm_endpoints.id"), nullable=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id"))
    num_users = Column(Integer, nullable=True)
    percentage_of_questions = Column(Integer, nullable=True)
    order_of_questions = Column(String, nullable=True)
    ts = Column(DateTime, default=datetime.utcnow)
    simulation_id = Column(String)
    status = Column(String)

    # Define relationships
    dataset = relationship("Dataset", back_populates="evaluation_profiles")
    llm_endpoint = relationship("LLMEndpoint", back_populates="evaluation_profiles")
    assessments = relationship("Assessments", back_populates="evaluation_profiles")
    evaluation_runs = relationship(
        "EvaluationRuns", back_populates="evaluation_profiles"
    )

class EvaluationRuns(Base):
    __tablename__ = "evaluation_runs"

    id = Column(Integer, primary_key=True, index=True)
    orgid = Column(String)
    evaluation_profile_id = Column(Integer, ForeignKey("evaluation_profiles.id"))
    ts = Column(DateTime, default=datetime.utcnow)
    score = Column(Float)
    run_status = Column(String)
    evaluation_id = Column(String, nullable=True)

    # Define relationships
    evaluation_profiles = relationship(
        "EvaluationProfiles", back_populates="evaluation_runs"
    )
    assessments = relationship("Assessments", back_populates="evaluation_runs")

class Assessments(Base):
    __tablename__ = "assessments"

    id = Column(Integer, primary_key=True, index=True)
    simulation_userid = Column(String)
    orgid = Column(String)
    dataset_id = Column(Integer, ForeignKey("datasets.id"))
    llm_endpoint_id = Column(Integer, ForeignKey("llm_endpoints.id"), nullable=True)
    qa_data_id = Column(Integer, ForeignKey("qa_data.id"))
    evaluation_profile_id = Column(Integer, ForeignKey("evaluation_profiles.id"))
    run_id = Column(Integer, ForeignKey("evaluation_runs.id"))
    ts = Column(DateTime, default=datetime.utcnow)
    score = Column(Float)
    score_reason = Column(String, nullable=True)
    endpoint_response = Column(String)
    evaluation_id = Column(String)
    verified_reference_context = Column(String, nullable=True)
    chunks_retrieved = Column(JSON, nullable=True)
    min_retrieval_score = Column(Float, nullable=True)
    max_retrieval_score = Column(Float, nullable=True)
    avg_retrieval_score = Column(Float, nullable=True)

    # Define relationships
    dataset = relationship("Dataset", back_populates="assessments")
    llm_endpoint = relationship("LLMEndpoint", back_populates="assessments")
    qa_data = relationship("QAData", back_populates="assessments")
    evaluation_profiles = relationship(
        "EvaluationProfiles", back_populates="assessments"
    )
    evaluation_runs = relationship("EvaluationRuns", back_populates="assessments")