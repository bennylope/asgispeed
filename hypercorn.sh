#!/usr/bin/env sh

# The type of worker to use. Options include asyncio, uvloop (pip install hypercorn[uvloop]),
# and trio (pip install hypercorn[trio]).

hypercorn asgispeed.asgi:application -b 127.0.0.1:8000 -w 4 -k asyncio
