# Use a lightweight official Python image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy only the requirements file first for better build caching
COPY requirements.txt /app/requirements.txt

# Install dependencies using explicit absolute path
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy the rest of your application code
COPY . /app/

# Expose the port (FastAPI default)
EXPOSE 8000

# Command to run your FastAPI application using Uvicorn
CMD ["python", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
