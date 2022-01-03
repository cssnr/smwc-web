import logging
import shutil
from celery import shared_task

logger = logging.getLogger('app')


@shared_task(autoretry_for=(Exception,), retry_kwargs={'max_retries': 1, 'countdown': 180})
def cleanup_hack(path):
    logger.debug('cleanup_hack: executed')
    logger.debug('path: %s', path)
    return shutil.rmtree(path)
