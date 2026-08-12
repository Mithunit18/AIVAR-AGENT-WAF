FROM python:3.10-slim

# Create a non-root user
RUN useradd --create-home agentuser

# Set working directory
WORKDIR /app

# Install dependencies first (for caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Adjust permissions
RUN chown -R agentuser:agentuser /app

# Switch to non-root user
USER agentuser

# Run simulation unbuffered
ENTRYPOINT ["python", "-u", "run_simulation.py"]
