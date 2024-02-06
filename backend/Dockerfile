FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt --no-cache-dir

COPY last_hackaton/ .

CMD ["gunicorn", "last_hackaton.wsgi:application", "--bind", "0:8000"]