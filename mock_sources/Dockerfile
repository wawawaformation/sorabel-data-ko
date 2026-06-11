FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir "fastapi>=0.115,<0.120" "uvicorn[standard]>=0.30,<0.40"

COPY app.py /app/app.py

EXPOSE 8011
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8011"]
