FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml .
RUN pip install -e .

COPY . .

ENV PORT=8080
EXPOSE 8080

CMD ["python", "adk_app.py"]
