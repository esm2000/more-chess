FROM --platform=linux/amd64 python:3

WORKDIR /app
COPY . .

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r backend/requirements.txt 

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH="/app/backend"

RUN pytest
CMD ["python", "backend/server.py"]