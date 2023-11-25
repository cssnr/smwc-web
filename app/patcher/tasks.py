import logging
import shutil
from celery import shared_task

logger = logging.getLogger('celery')


@shared_task(autoretry_for=(Exception,), retry_kwargs={'max_retries': 1, 'countdown': 300})
def cleanup_hack(path):
    logger.debug('cleanup_hack: path: %s', path)
    return shutil.rmtree(path)
