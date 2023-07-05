#!/usr/bin/env sh

set -ex

if echo "${*}" | grep -q "gun";then
    if [ -n "${DJANGO_SUPERUSER_PASSWORD}" ] &&
    [ -n "${DJANGO_SUPERUSER_USERNAME}" ] &&
    [ -n "${DJANGO_SUPERUSER_EMAIL}" ];then
        python manage.py createsuperuser --noinput || :
    fi
    python manage.py collectstatic --noinput
fi

exec "$@"
