# Use the official Python image as the base image
FROM python:3.9

# Set the working directory in the container
WORKDIR /app

# Copy the application code into the container
COPY . /app

# Install the required dependencies
RUN pip install -r requirements.txt

# Set environment variables
ENV FLASK_APP=ingesting_service.py
ENV FLASK_ENV=development
ENV FLASK_DEBUG=1

# Run the Flask app
CMD ["python", "ingesting_service.py"]
