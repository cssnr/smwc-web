FROM nginx:stable-alpine
ENV TZ=America/Los_Angeles

RUN apk add --no-cache tzdata

COPY nginx.conf /etc/nginx/nginx.conf
