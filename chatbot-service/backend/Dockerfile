FROM python:3.11-slim

RUN apt-get update && apt-get upgrade -y && apt-get install -y gcc libffi-dev \
	&& apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]