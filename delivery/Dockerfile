FROM python:3.9

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

# Make port 80 available to the world outside this container
# You may not need this since your script doesn't expose any ports
# EXPOSE 80

# Run the delivery worker script when the container launches
CMD ["python", "delivery_service.py"]