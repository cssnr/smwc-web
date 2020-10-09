from __future__ import absolute_import, unicode_literals
import logging
import shutil
from celery.decorators import task

logger = logging.getLogger('celery')


@task(name='cleanup_hack')
def cleanup_hack(path):
    logger.info('cleanup_hack: executed')
    logger.info('path: {}'.format(path))
    return shutil.rmtree(path)
