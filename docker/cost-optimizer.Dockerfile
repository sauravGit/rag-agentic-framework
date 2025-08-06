# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code into the container
COPY ./src /app/src

# Make port 8006 available to the world outside this container
EXPOSE 8006

# Run the application
CMD ["uvicorn", "src.cost_optimization.main:app", "--host", "0.0.0.0", "--port", "8006"]
