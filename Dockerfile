# Raspberry pi  will use Debian:
FROM arm64v8/python:3.10-slim



# Installation of python:
WORKDIR /app
RUN apt-get update && apt install -y python3-venv python3-pip

# Create a environnement 
RUN python3 -m venv /app/venv

# Upgrade pip:
RUN /app/venv/bin/pip install --upgrade pip 

ENV PATH="/app/venv/bin:$PATH"

# Copy all the files into /app
COPY . /app

# Install the dependencies:
RUN pip install -r requirements.txt

# Run Jarvis:
CMD ["python3", "main.py"] 