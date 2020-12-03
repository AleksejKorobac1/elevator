from django.db import models
from datetime import datetime


class Elevator(models.Model):
    current_floor = models.IntegerField(default=1)
    action = models.IntegerField(default=0)  # -1 - doors opening, -2 - doors closing, 0 - idle, other int - destination
    movement_speed = models.IntegerField(default=1)
    door_speed = models.IntegerField(default=2)
    active = models.IntegerField(default=1)
    request = models.CharField(max_length=10, default='[]')


class Building(models.Model):
    floor_count = models.IntegerField(default=2)
    active_elevators = models.IntegerField(default=2)
    requests = models.CharField(max_length=50, default='[]')


class Log(models.Model):
    elevator_id = models.IntegerField(default=0)
    action = models.CharField(max_length=100, default='')
    position = models.IntegerField(default=0)
    destination = models.IntegerField(default=0)
    time = models.DateTimeField(default=datetime.now().replace(microsecond=0))
