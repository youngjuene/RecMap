FROM python:3.11-slim
FROM gboeing/osmnx:latest

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

EXPOSE 80

CMD ["streamlit", "run", "app.py", "--server.address", "0.0.0.0", "--server.port", "80"]