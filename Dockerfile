# official Python runtime as the base image
FROM python:3.12.2-slim

# environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# working directory in the container
WORKDIR /app

# copy the dependencies file to the working directory
COPY requirements.txt .

# install any dependencies
RUN pip install --no-cache-dir -r requirements.txt

# copy the rest of the application code to the working directory
COPY . .

# expose port 8000 to allow external access
EXPOSE 8000

# command to run the FastAPI application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
