FROM python:3.11-slim

# Set work directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN python -m venv /opt/venv \
    && /opt/venv/bin/pip install --upgrade pip \
    && /opt/venv/bin/pip install -r requirements.txt

# Copy your project files
COPY . .

# Use the virtual environment
ENV PATH="/opt/venv/bin:$PATH"

# Expose the port
EXPOSE 8080

# Run the app (removed --reload flag for production)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]