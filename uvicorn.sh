#!/usr/bin/env sh

uvicorn asgispeed.asgi:application ${PORT:8098} --workers 4
