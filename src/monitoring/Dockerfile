
FROM python:3.11-slim

WORKDIR /app

COPY requirements-monitoring.txt .

RUN pip install --no-cache-dir -r requirements-monitoring.txt

COPY src/monitoring/dashboard.py .

EXPOSE 8501

CMD ["streamlit", "run", "dashboard.py", "--server.address=0.0.0.0", "--server.port=8501"]
