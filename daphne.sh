#!/usr/bin/env sh

daphne asgispeed.asgi:application ${PORT:8098}
