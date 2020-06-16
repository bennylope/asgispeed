from django.urls import path
from . import views

urlpatterns = [
    path("", views.index),
    path("simple-sleep", views.simple_sleep, name="simple-sleep"),
    path("waiting-sequentially/", views.waiting_in_sequence, name="waiting-sequentially"),
    path("waiting-concurrently/", views.waiting_in_parallel, name="waiting-concurrently"),
    path("sync-hello-world/", views.sync_hello_world, name="sync-hello-world"),
    path("async-hello-world/", views.async_hello_world, name="async-hello-world"),
    path("sync-list/", views.sync_list, name="sync-list"),
    path("async-list/<int:sleep>/", views.async_list, name="async-list"),
    path("async-update/<int:sleep>/", views.async_update, name="async-update"),
    path(
        "async-cbv-detail/<int:pk>/<int:sleep>/",
        views.AsyncDetailView.as_view(),
        name="async-detail-view",
    ),
    path("async-save/<int:id>/<int:sleep>/", views.async_save, name="async-save"),
    path("api-calling/<int:sleep>/", views.api_calling, name="api-calling"),
]
