# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory to /app
WORKDIR /app

# Install system dependencies, install pipenv, and then install project dependencies
RUN apt-get update && apt-get install -y libpq-dev curl build-essential && \
    pip install --upgrade pip && \
    pip install poetry

# Copy the current directory contents into the container at /app
COPY . /app  

RUN poetry install && \
    mkdir -p /app/qa_generator_outputs && \
    mkdir -p /app/qa_generator_uploads

# Expose the port that the application will run on
EXPOSE 8000

# Define the command to run your application
CMD ["poetry", "run", "uvicorn", "src.service:app", "--host", "0.0.0.0", "--port", "8000"]