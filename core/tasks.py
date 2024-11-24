from datetime import datetime
from logging import getLogger

from celery import shared_task

from core.utils.scheduler import Scheduler

logger = getLogger(__name__)


@shared_task
def consume_enqueued_deployments() -> None:
    """ """

    logger.info(f"[Task]: Process InQueued Deployment Task Started at {datetime.now()}")
    Scheduler().schedule_deployment()
    logger.info(f"[Task]: Process InQueued Deployment Task Completed at {datetime.now()}")


@shared_task
def consume_terminal_deployments() -> None:
    """ """

    logger.info(f"[Task]: Deployment Cleanup Task Started at {datetime.now()}")
    Scheduler().cleanup_completed_deployments()
    logger.info(f"[Task]: Deployment Cleanup Task Completed at {datetime.now()}")
