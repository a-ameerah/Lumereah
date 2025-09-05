# gunicorn.conf.py
workers = 1  # Only one worker to save memory
threads = 2  # Light threading
timeout = 120  # Longer timeout for AI processing
worker_class = "sync"  # Simple worker type