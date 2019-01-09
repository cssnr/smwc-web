from __future__ import absolute_import, unicode_literals
import logging
from celery import task

logger = logging.getLogger(__name__)


@task(name='test_task')
def test_task():
    logger.info('test_task: executed')
    return 'test_task: success'
