FROM python:3.11-slim

# Create non-root user required by Hugging Face Spaces Docker runtime
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PORT=7860 \
    API_PORT=7860 \
    NEO4J_URI="embedded://exports/lta_knowledge_graph.json"

WORKDIR /app

COPY --chown=user requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /app/requirements.txt

COPY --chown=user src /app/src
COPY --chown=user exports /app/exports

EXPOSE 7860

CMD ["uvicorn", "src.api.server:app", "--host", "0.0.0.0", "--port", "7860"]
