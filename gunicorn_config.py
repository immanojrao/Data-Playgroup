"""
Gunicorn Configuration for Production Deployment
Place this file in your project root directory
"""
import multiprocessing
import os

# Server socket
bind = "0.0.0.0:5000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1  # Recommended formula
worker_class = "gthread"  # Use threaded workers
threads = 2  # Threads per worker
worker_connections = 1000
max_requests = 1000  # Restart workers after this many requests (prevents memory leaks)
max_requests_jitter = 50
timeout = 120  # Request timeout in seconds
keepalive = 5  # Keep-alive timeout

# Logging
accesslog = "logs/access.log"
errorlog = "logs/error.log"
loglevel = "info"  # debug, info, warning, error, critical
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "data_analyzer"

# Server mechanics
daemon = False  # Set to True to run as daemon
pidfile = "/tmp/data_analyzer.pid"
umask = 0
user = None  # Run as this user (None = current user)
group = None  # Run as this group (None = current group)
tmp_upload_dir = None

# SSL (if using HTTPS)
# keyfile = "/path/to/keyfile"
# certfile = "/path/to/certfile"
