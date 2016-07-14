from django.db import models
from django.conf import settings

divisions = (
    ('1', 'Division 1'),
    ('2', 'Division 2')
)
penalty = 10


class Question(models.Model):
    title = models.CharField(max_length=100)
    body = models.TextField()
    division = models.CharField(max_length=1, choices=divisions)

    def __str__(self):
        return self.title

    def get_submissions(self, team):
        return self.submission_set.filter(team=team).order_by('-submission_time')

    def is_solved(self, team):
        return self.submission_set.filter(team=team, correct=True).count() > 0

    def get_num_submissions(self, team):
        return self.submission_set.filter(team=team).count()

    def get_penalty(self, team):
        return self.submission_set.filter(team=team, correct=False).count() * penalty


class TestCase(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    standard_in = models.TextField()
    standard_out = models.TextField()
    error_viewable = models.BooleanField()


class Team(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    team_name = models.CharField(max_length=100)
    division = models.CharField(max_length=1, choices=divisions)

    def __str__(self):
        return self.team_name + "(" + self.division + ")"


class Submission(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    language = models.CharField(max_length=20)
    code = models.TextField()
    correct = models.BooleanField()
    submission_time = models.DateTimeField()
