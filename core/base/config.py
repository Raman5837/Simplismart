from typing import Dict

CELERY_BEAT_SCHEDULE_CONFIG: Dict[str, Dict] = {
    "process_enqueued_deployments": {
        "task": "core.tasks.consume_enqueued_deployments",
        "schedule": 60.0,  # Runs every 60 seconds
    },
    "process_terminal_deployments": {
        "task": "core.tasks.consume_terminal_deployments",
        "schedule": 120.0,  # Runs every 2 minutes
    },
}


# python -m celery -A hypervisor beat --loglevel=info
# python -m celery -A hypervisor worker --loglevel=info
