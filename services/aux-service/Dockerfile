FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

ENV AUX_VERSION=0.0.1

CMD ["gunicorn", "app:app", "-b", "0.0.0.0:5000"]
