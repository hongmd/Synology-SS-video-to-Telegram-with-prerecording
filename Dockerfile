# syntax=docker/dockerfile:1

FROM python:alpine

# Create non-root user for security
RUN addgroup -g 1000 appuser && adduser -D -u 1000 -G appuser appuser

# Setup Python virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH" PIP_NO_CACHE_DIR=off

# Copy requirements first (for better layer caching)
COPY requirements.txt .

# Install dependencies
RUN pip3 install --upgrade pip setuptools-rust wheel && \
    pip3 install -r requirements.txt && \
    rm -rf /root/.cache /root/.cargo

# Create app directory and set permissions
WORKDIR /app
RUN chown -R appuser:appuser /app

# Copy application code
COPY --chown=appuser:appuser ["src/main.py", "/app/"]

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 7878

# Health check - verify Flask is responding
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost:7878/webhookcam || exit 1

# Start application with optimized workers
# Use 2-4 workers depending on CPU cores
CMD ["gunicorn", "--bind", "0.0.0.0:7878", "--workers", "2", "--worker-class", "sync", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-", "main:app"]