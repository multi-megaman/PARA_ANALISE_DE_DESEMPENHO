


# The builder image, used to build the virtual environment
FROM python:3.9.19-alpine3.20 as builder

# RUN pip install --upgrade pip --no-cache-dir
COPY requirements.txt ./
RUN pip install -r requirements.txt --no-cache-dir

WORKDIR /app

COPY . .