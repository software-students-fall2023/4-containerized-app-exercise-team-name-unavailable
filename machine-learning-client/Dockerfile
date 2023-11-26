FROM python:3.10.4-slim-buster

WORKDIR /machine-learning-client

COPY /Pipfile .
COPY /Pipfile.lock .


RUN pip install pipenv
RUN apt-get update
RUN apt-get install -y llvm-dev
RUN pipenv install --system --deploy --verbose

COPY /machine-learning-client/ml_client.py .

CMD ["python", "ml_client.py"]