FROM python:3.10.4-slim-buster

COPY /Pipfile .
COPY /Pipfile.lock .

RUN pip install pipenv
RUN apt-get update
RUN apt-get install -y llvm-dev
RUN pipenv install --system --deploy --verbose

# Stuff in web-app/ is copied to the root directory of the container, not web-app itself
COPY /web-app/ /

# NOTE: You have to mount a directory containing cert.pem and key.pem to /certs.
# Accomplish this using `volumes` in compose.yaml.
CMD ["python", "app.py"]