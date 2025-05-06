FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install uv
RUN pip install uv

# Copy requirements
COPY pyproject.toml .

# Create virtual environment and install dependencies
RUN uv venv
RUN uv pip install -e .

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Set environment variables
ENV PYTHONPATH=/app
ENV ENVIRONMENT=production
ENV DEBUG=false

# Run the application
CMD ["uvicorn", "src.openai_compatible_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
