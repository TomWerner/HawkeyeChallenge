from django.db import models
from django.conf import settings

divisions = (
    ('1', 'Division 1'),
    ('2', 'Division 2')
)


class Question(models.Model):
    title = models.CharField(max_length=100)
    body = models.TextField()
    division = models.CharField(max_length=1, choices=divisions)


class Team(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    team_name = models.CharField(max_length=100)
    division = models.CharField(max_length=1, choices=divisions)


