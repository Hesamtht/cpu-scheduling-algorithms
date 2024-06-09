# scheduler/models.py

from django.db import models

class Process(models.Model):
    name = models.CharField(max_length=100)
    arrival_time = models.IntegerField()
    burst_time = models.IntegerField()
    priority = models.IntegerField(default=0)

    def __str__(self):
        return self.name
