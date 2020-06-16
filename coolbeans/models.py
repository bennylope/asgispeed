from django.db import models


class Entry(models.Model):
    message = models.TextField()
    count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.message}: {self.count}"
