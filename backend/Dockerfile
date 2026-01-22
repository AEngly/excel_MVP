# Backend Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install uv
RUN pip install uv

# Copy dependency files
COPY pyproject.toml ./
COPY requirements.txt ./

# Install dependencies with uv
RUN uv pip install --system -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 3001

# Run the application
CMD ["uv", "run", "python", "main.py"]
