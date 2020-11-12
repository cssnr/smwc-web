import logging
import shutil
from celery.decorators import task

logger = logging.getLogger('app')


@task(autoretry_for=(Exception,), retry_kwargs={'max_retries': 1, 'countdown': 120})
def cleanup_hack(path):
    logger.debug('cleanup_hack: executed')
    logger.debug('path: %s', path)
    return shutil.rmtree(path)
