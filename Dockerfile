FROM python:3
ADD ./src/mlp.py
RUN pip install -r requirements.txt