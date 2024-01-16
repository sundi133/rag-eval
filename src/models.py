from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()

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

    # Define relationships
    qa_data = relationship("QAData", back_populates="dataset")
    evaluations = relationship("Evaluation", back_populates="dataset")
    simulation_profiles = relationship("SimulationProfile", back_populates="dataset")


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
    evaluations = relationship("Evaluation", back_populates="qa_data")


class LLMEndpoint(Base):
    __tablename__ = "llm_endpoints"

    id = Column(Integer, primary_key=True, index=True)
    userid = Column(String)
    orgid = Column(String)
    name = Column(String, index=True)
    endpoint_url = Column(String)
    ts = Column(DateTime, default=datetime.utcnow)
    access_token = Column(String)
    payload_format = Column(String)
    payload_user_key = Column(String)
    payload_message_key = Column(String)
    payload_response_key = Column(String)
    http_method = Column(String)
    requests_per_minute = Column(Integer)

    evaluations = relationship("Evaluation", back_populates="llm_endpoint")
    simulation_profiles = relationship(
        "SimulationProfile", back_populates="llm_endpoint"
    )



class SimulationProfile(Base):
    __tablename__ = "simulation_profiles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    userid = Column(String)
    orgid = Column(String)
    endpoint_url_id = Column(Integer, ForeignKey("llm_endpoints.id"))
    dataset_id = Column(Integer, ForeignKey("datasets.id"))
    num_users = Column(Integer)
    percentage_of_questions = Column(Integer)
    order_of_questions = Column(String)
    ts = Column(DateTime, default=datetime.utcnow)
    simulation_id = Column(String)
    status = Column(String)

    # Define relationships
    dataset = relationship("Dataset", back_populates="simulation_profiles")
    llm_endpoint = relationship("LLMEndpoint", back_populates="simulation_profiles")
    evaluations = relationship("Evaluation", back_populates="simulation_profile")
    simulation_runs = relationship("SimulationRuns", back_populates="simulation_profile")

class SimulationRuns(Base):
    __tablename__ = "simulation_runs"

    id = Column(Integer, primary_key=True, index=True)
    orgid = Column(String)
    simulation_id = Column(Integer, ForeignKey("simulation_profiles.id"))
    ts = Column(DateTime, default=datetime.utcnow)
    score = Column(Float)
    run_status = Column(String)

    # Define relationships
    simulation_profile = relationship("SimulationProfile", back_populates="simulation_runs")
    evaluation = relationship("Evaluation", back_populates="simulation_run")

class Evaluation(Base):
    __tablename__ = "evaluations"

    id = Column(Integer, primary_key=True, index=True)
    simulation_userid = Column(String)
    orgid = Column(String)
    dataset_id = Column(Integer, ForeignKey("datasets.id"))
    llm_endpoint_id = Column(Integer, ForeignKey("llm_endpoints.id"))
    qa_data_id = Column(Integer, ForeignKey("qa_data.id"))
    simulation_id = Column(Integer, ForeignKey("simulation_profiles.id"))
    simulation_run_id = Column(Integer, ForeignKey("simulation_runs.id"))
    ts = Column(DateTime, default=datetime.utcnow)
    score = Column(Float)
    endpoint_response = Column(String)
    evaluation_id = Column(String)

    # Define relationships
    dataset = relationship("Dataset", back_populates="evaluations")
    llm_endpoint = relationship("LLMEndpoint", back_populates="evaluations")
    qa_data = relationship("QAData", back_populates="evaluations")
    simulation_profile = relationship("SimulationProfile", back_populates="evaluations")
    simulation_run = relationship("SimulationRuns", back_populates="evaluation")
