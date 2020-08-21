FROM python:3.8.5-slim-buster
WORKDIR /miko_dal

COPY ./requirements.txt ./
RUN pip install -r ./requirements.txt

COPY . ./
CMD python3 miko_rmq_sub.py