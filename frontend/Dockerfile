FROM python:3.11-slim

WORKDIR /app

# Install dependencies with compatible versions
RUN pip install --no-cache-dir \
    gradio==4.19.2 \
    huggingface_hub==0.20.3 \
    httpx \
    python-multipart

# Copy application code
COPY . .

EXPOSE 7860 7861

CMD ["python", "-m", "public_app.main"]