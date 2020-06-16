# -*- coding: utf-8 -*-

"""
A choice selection of [mostly] async views
"""

import asyncio
import random
import time
from functools import update_wrapper

from asgiref import sync
from django import shortcuts
from django.db.models import F
from django.http import JsonResponse
from django.utils.decorators import classonlymethod
from django.views.generic import DetailView

from . import async_helpers as helpers
from . import models


def chunks(seq, size):
    for pos in range(0, len(seq), size):
        yield seq[pos : pos + size]


async def index(request):
    """The home page"""
    return await helpers.render(request, "index.html")


def sync_list(request):
    all_entries = models.Entry.objects.all()
    return shortcuts.render(request, "entries.html", {"entries": all_entries})


def simple_sleep(request):
    time.sleep(0.25)
    return JsonResponse({"result": "ok"})


async def async_list(request, sleep=1000):
    all_entries = models.Entry.objects.all()
    # print(all_entries) - BAD!
    sleep_in_seconds = sleep / 1000
    api_calls = await collected_api_calls(sleep=sleep_in_seconds)
    return await helpers.render(
        request,
        "entries.html",
        {
            "entries": all_entries,
            "sleep_in_seconds": sleep_in_seconds,
            "api_calls": api_calls,
        },
    )


async def async_update(request, sleep=1000):
    all_entries = models.Entry.objects.all()
    # print(all_entries) - BAD!
    sleep_in_seconds = sleep / 1000
    api_calls = await collected_api_calls(sleep=sleep_in_seconds)

    @sync.sync_to_async
    def update_entries():
        """The async-unsafe code can be used in a closure"""
        models.Entry.objects.update(count=F("count") + 1)

    await update_entries()

    return await helpers.render(
        request,
        "entries.html",
        {
            "entries": all_entries,
            "sleep_in_seconds": sleep_in_seconds,
            "api_calls": api_calls,
        },
    )


async def async_save(request, id, sleep=1000):
    sleep_in_seconds = sleep / 1000
    api_calls = await collected_api_calls(sleep=sleep_in_seconds)

    entry = await helpers.get_object_or_404(models.Entry, pk=id)

    new_text = request.GET.get("text", "")
    if new_text:
        entry.message = new_text
        entry.count += 1

        @sync.sync_to_async
        def save():
            entry.save()
            return entry

        # await helpers.partial_executor(entry.save)

        await save()

    api_calls += await collected_api_calls(sleep=sleep_in_seconds)
    return await helpers.render(
        request,
        "entry.html",
        {"entry": entry, "sleep_in_seconds": sleep_in_seconds, "api_calls": api_calls,},
    )


class AsyncDetailView(DetailView):
    model = models.Entry
    template_name = "entry.html"

    @classonlymethod
    def as_view(cls, **initkwargs):
        """Main entry point for a request-response process."""
        for key in initkwargs:
            if key in cls.http_method_names:
                raise TypeError(
                    "The method name %s is not accepted as a keyword argument "
                    "to %s()." % (key, cls.__name__)
                )
            if not hasattr(cls, key):
                raise TypeError(
                    "%s() received an invalid keyword %r. as_view "
                    "only accepts arguments that are already "
                    "attributes of the class." % (cls.__name__, key)
                )

        async def view(request, *args, **kwargs):
            self = cls(**initkwargs)
            self.setup(request, *args, **kwargs)
            if not hasattr(self, "request"):
                raise AttributeError(
                    "%s instance has no 'request' attribute. Did you override "
                    "setup() and forget to call super()?" % cls.__name__
                )
            return await self.dispatch(request, *args, **kwargs)

        view.view_class = cls
        view.view_initkwargs = initkwargs

        # take name and docstring from class
        update_wrapper(view, cls, updated=())

        # and possible attributes set by decorators
        # like csrf_exempt from dispatch
        update_wrapper(view, cls.dispatch, assigned=())
        return view

    def dispatch(self, request, *args, **kwargs):
        # Try to dispatch to the right method; if a method doesn't exist,
        # defer to the error handler. Also defer to the error handler if the
        # request method isn't on the approved list.
        if request.method.lower() in self.http_method_names:
            handler = getattr(
                self, request.method.lower(), self.http_method_not_allowed
            )
        else:
            handler = self.http_method_not_allowed
        return handler(request, *args, **kwargs)

    @sync.sync_to_async
    def get_object(self, queryset=None):
        return super().get_object(queryset)

    async def get(self, request, *args, **kwargs):
        self.object = await self.get_object()
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)


async def api_call(sleep=0.3):
    await asyncio.sleep(sleep)
    print(f"Heyo! slept for {sleep}")
    return {"result": random.random()}


async def collected_api_calls(total=30, set_size=5, sleep=0.3):
    results = []
    for chunk in chunks(range(total), set_size):
        partial_results = await asyncio.gather(*[api_call(sleep) for _ in chunk])
        results += partial_results
    return results


def sync_hello_world(request):
    return shortcuts.render(request, "hello.html")


async def async_hello_world(request):
    return shortcuts.render(request, "hello.html")


async def api_calling(request, sleep=1000):
    """

    Args:
        request:
        sleep: sleep time in ms

    Returns:

    """
    await collected_api_calls(total=30, set_size=5, sleep=sleep / 1000)
    return JsonResponse({"result": "ok"})


async def waiting_in_sequence(request, sleep=500):
    start = time.time()
    sleep_in_seconds = sleep / 1000
    await collected_api_calls(total=30, set_size=5, sleep=sleep_in_seconds)
    await collected_api_calls(total=30, set_size=5, sleep=sleep_in_seconds)
    finished = time.time() - start
    return await helpers.render(
        request,
        "waiting.html",
        {"count": 2, "finished": finished, "slept": sleep_in_seconds, "method": "sequentially"},
    )


async def waiting_in_parallel(request, sleep=500):
    start = time.time()
    sleep_in_seconds = sleep / 1000
    initial = asyncio.create_task(
        collected_api_calls(total=30, set_size=5, sleep=sleep_in_seconds)
    )
    subsequent = asyncio.create_task(
        collected_api_calls(total=30, set_size=5, sleep=sleep_in_seconds)
    )
    await asyncio.gather(
        initial, subsequent,
    )
    finished = time.time() - start
    return await helpers.render(
        request,
        "waiting.html",
        {"count": 2, "finished": finished, "slept": sleep_in_seconds, "method": "concurrently"},
    )
