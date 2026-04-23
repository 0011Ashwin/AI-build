FROM python:3.11-slim

WORKDIR /app

# Install dependencies from root
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all required modules
COPY agents/ ./agents/
COPY shared/ ./shared/
COPY app/ ./app/

# Set working directory to app for execution
WORKDIR /app/app

ENV PORT=8080
ENV PYTHONPATH=/app
EXPOSE 8080

CMD ["python", "main.py"]
