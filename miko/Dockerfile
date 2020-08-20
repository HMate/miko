FROM python:3.8.5-slim-buster
WORKDIR /miko

COPY ./requirements.txt ./
RUN pip install -r ./requirements.txt

COPY . ./
CMD python3 -m flask run --host=0.0.0.0 --port=5000