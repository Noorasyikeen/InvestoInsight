FROM python:3.10.6-buster

# Create the /app directory
RUN mkdir /app

# Copy the file
COPY "/Users/huiye/code/data-science-bc-970805-67a6d0564b74.json" /app/credentials.json

# Change permissions to make it more permissive
RUN chmod 644 /app/credentials.json


ENV GOOGLE_APPLICATION_CREDENTIALS="/Users/huiye/code/data-science-bc-970805-67a6d0564b74.json"

WORKDIR /prod

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY stockprice stockprice
COPY setup.py setup.py
RUN pip install .

COPY Makefile Makefile
# RUN make reset_local_files

CMD uvicorn stockprice.api.fast:app --host 0.0.0.0 --port $PORT
