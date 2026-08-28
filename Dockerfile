# ==============================================================================
# Dockerfile: SaaS Password-Reset Service
# ==============================================================================
# DevOps Concept - Containerisation:
# Containers package code together with its runtime, system tools, and dependencies,
# solving the classic "it works on my machine" problem. This guarantees consistency
# across development, CI/CD runners, and production hosting environments.
# ==============================================================================

# Step 1: Base Image
# Use official lightweight Python 3.13 slim image to minimise image size and attack surface
FROM python:3.13-slim

# Step 2: Set working directory inside container
WORKDIR /app

# Step 3: Install dependencies
# Copy requirements first to leverage Docker layer caching (dependencies are cached unless requirements.txt changes)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Step 4: Copy application source code and tests into container
COPY . .

# Step 5: Expose application port
# Informs container runtimes that Flask listens on TCP port 5000
EXPOSE 5000

# Step 6: Environment Configuration
ENV PYTHONUNBUFFERED=1 \
    FLASK_APP=app:create_app

# Step 7: Container Entrypoint Command
# Bind Flask to 0.0.0.0 so external container traffic can reach port 5000
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=5000"]
