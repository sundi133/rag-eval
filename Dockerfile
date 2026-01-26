# Use an official Python runtime as a parent image
DOCKERFILE = r"""
FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y libpq-dev curl build-essential && \
    pip install --upgrade pip && \
    pip install poetry==1.6.1

COPY . /app  

RUN poetry install && \
    mkdir -p /app/qa_generator_outputs && \
    mkdir -p /app/qa_generator_uploads

EXPOSE 8000 8001
# 🔒 VOTAL.AI Security Fix: Development server configuration: binds to 0.0.0.0 and enables --reload [CWE-1004] - MEDIUM

CMD ["poetry", "run", "uvicorn", "src.service:app", "--host", "127.0.0.1", "--port", "8000"] # fixed: removed --reload and bind to localhost only
""".lstrip()