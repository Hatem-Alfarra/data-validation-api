import multiprocessing

# Network
bind = "127.0.0.1:8000"  # Address and port Gunicorn listens on

# Workers
# Standard formula: 2 * CPU cores + 1
workers = multiprocessing.cpu_count() * 2 + 1
# Use Uvicorn workers for ASGI support
worker_class = "uvicorn.workers.UvicornWorker"

# Timeouts
timeout = 30
keepalive = 5

# Logging
# Log level: debug, info, warning, error, critical
loglevel = "info"
# Log to stdout
accesslog = "-"
errorlog = "-"

# Process naming
proc_name = "data_validation_api"