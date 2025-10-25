
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt pyproject.toml README.md /app/
RUN pip install -U pip && pip install -r requirements.txt && pip install -e .
COPY src ./src
CMD ["python", "-m", "src.mcpws.agents.crew_agent"]
