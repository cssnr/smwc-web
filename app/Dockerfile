FROM python:3.8-alpine
ENV TZ=America/Los_Angeles

RUN apk add --update --no-cache \
    alpine-sdk \
    build-base \
    mariadb-client \
    mysql-dev \
    python3-dev \
    tzdata

RUN addgroup -g 1000 app && \
    adduser -S -H -h /app -s /sbin/nologin -u 1000 -G app app

WORKDIR /app

ADD --chown=app:app requirements.txt .
RUN python -m pip install --no-cache-dir --upgrade pip && \
    python -m pip install --no-cache-dir -r requirements.txt

RUN mkdir -p /app /data && chown app:app /app /data
ADD --chown=app:app . .

USER app
ENTRYPOINT ["sh", "docker-entrypoint.sh"]
