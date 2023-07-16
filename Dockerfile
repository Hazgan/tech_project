FROM tiangolo/uvicorn-gunicorn:python3.10

COPY ./app /app

RUN pip install -r /app/requirements.txt

