import multiprocessing

import gunicorn

gunicorn.SERVER: str = "Platform"
gunicorn.SERVER_SOFTWARE: str = "Omni"

timeout: int = 60
bind: str = "0.0.0.0:8000"
workers: int = multiprocessing.cpu_count() * 4
threads: int = multiprocessing.cpu_count() * 4
