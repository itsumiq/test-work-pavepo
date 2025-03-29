FROM python:3.13.1-slim
WORKDIR /app/
COPY ./requirements.txt /app/
RUN pip install --upgrade --no-cache-dir -r requirements.txt
COPY ./app /app/app/
