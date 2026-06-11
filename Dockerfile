version: "3.9"

services:

  backend:
    build: .
    container_name: risk-backend
    ports:
      - "8000:8000"

  frontend:
    image: python:3.10-slim
    container_name: risk-frontend
    working_dir: /app
    volumes:
      - .:/app
    command: bash -c "pip install -r requirements.txt && streamlit run frontend/app.py --server.port 8501 --server.address 0.0.0.0"
    ports:
      - "8501:8501"