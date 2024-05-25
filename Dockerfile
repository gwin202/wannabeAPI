# Use the official Python image as base
FROM python:3.9.19

# Set the working directory inside the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install dependencies
RUN pip install -r requirement.txt 

# Expose port 8003 for FastAPI
EXPOSE 8003

# Run the FastAPI app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8003"]
