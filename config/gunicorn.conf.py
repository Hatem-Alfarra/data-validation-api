import multiprocessing

# Network
bind = "0.0.0.0:8000"                                                     # Address and port Gunicorn listens on

# Workers
workers = multiprocessing.cpu_count() * 2 + 1                               # Standard formula: 2 * CPU cores + 1
worker_class = "uvicorn.workers.UvicornWorker"                              # Use Uvicorn workers for ASGI support

# Timeouts
timeout = 30
keepalive = 5

# Logging
loglevel = "info"                                                           # Log level: debug, info, warning, error, critical
accesslog = "-"                                                             # log to stdout
errorlog = "-"                

# Process naming
proc_name = "data_validation_api"