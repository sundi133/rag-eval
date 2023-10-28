FROM python:3.9-slim

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install system dependencies, install pipenv, and then install project dependencies
RUN apt-get update && apt-get install -y libpq-dev curl build-essential && \
    pip install --upgrade pip && \
    pip install poetry && \
    poetry install

# Expose the port that the application will run on
EXPOSE 8002

# Define the command to run your application
CMD ["poetry", "run", "uvicorn", "src.sample_apps.app_2.main:app", "--host", "0.0.0.0", "--port", "8002"]
