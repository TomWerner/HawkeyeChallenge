from django.db import models

divisions = (
    ('1', 'Division 1'),
    ('2', 'Division 2')
)


class Question(models.Model):
    title = models.CharField(max_length=100)
    body = models.TextField()
    division = models.CharField(max_length=1, choices=divisions)


class Team(models.Model):
    login = models.CharField(max_length=100)
    team_name = models.CharField(max_length=100)
    division = models.CharField(max_length=1, choices=divisions)


