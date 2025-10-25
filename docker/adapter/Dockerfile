
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt pyproject.toml README.md /app/
RUN pip install -U pip && pip install -r requirements.txt && pip install -e .
COPY src ./src
EXPOSE 9100
CMD ["uvicorn", "src.mcpws.adapters.langflow_adapter:app", "--host", "0.0.0.0", "--port", "9100"]
