FROM python:3.10.4-alpine

WORKDIR .

COPY ../Pipfile .
COPY ../Pipfile.lock .

RUN pip install pipenv
RUN pipenv install --system --deploy

COPY ./ml_client.py .

CMD ["python", "ml_client.py"]