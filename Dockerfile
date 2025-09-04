FROM python:3.9-slim
WORKDIR /app
COPY . .
RUN pip install uv && uv venv && uv sync
CMD ["uv", "run", "word2img_mcp/start_mcp_server.py"]