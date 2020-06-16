# -*- coding: utf-8 -*-

"""
Shortcuts for dealing with synchronous code in async context
"""

from asgiref import sync
from django import shortcuts


@sync.sync_to_async
def get_object_or_404(klass, *args, **kwargs):
    return shortcuts.get_object_or_404(klass, *args, **kwargs)


@sync.sync_to_async
def render(
    request, template_name, context=None, content_type=None, status=None, using=None
):
    return shortcuts.render(
        request, template_name, context, content_type, status, using
    )


@sync.sync_to_async
def partial_executor(func, *args, **kwargs):
    return func(*args, **kwargs)
