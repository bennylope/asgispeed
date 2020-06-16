#!/usr/bin/env sh

#gunicorn asgispeed.wsgi:application ${PORT:8098} -w 4
gunicorn asgispeed.asgi:application -w 4 -k uvicorn.workers.UvicornWorker
