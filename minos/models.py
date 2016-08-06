from django.db import models
from django.conf import settings

divisions = (
    ('1', 'Division 1'),
    ('2', 'Division 2')
)
languages = (
    ('ace/mode/java', 'Java 7'),
    ('ace/mode/python', 'Python 2'),
    ('ace/mode/python-3', 'Python 3'),
    ('ace/mode/vbscript', 'Visual Basic'),
    ('ace/mode/c_cpp', 'C++ 11'),
    ('ace/mode/csharp', 'C#'),
)
penalty_in_minutes = 10


class Contest(models.Model):
    title = models.CharField(max_length=100)
    start_date = models.DateTimeField()
    active = models.BooleanField()

    def __str__(self):
        return self.title + (' - Active!' if self.active else '')


class Question(models.Model):
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    body = models.TextField()
    division = models.CharField(max_length=1, choices=divisions)

    def __str__(self):
        return self.title

    def get_latest_submission(self, team):
        submissions = self.submission_set.filter(team=team).order_by('-submission_time')
        if len(submissions) > 0:
            return submissions[0].code, submissions[0].language
        else:
            return '', 'ace/mode/python-3'

    def is_solved(self, team):
        return self.submission_set.filter(team=team, correct=True).count() > 0

    def get_num_submissions(self, team):
        return self.submission_set.filter(team=team).count()

    def get_penalty(self, team):
        return self.submission_set.filter(team=team, correct=False).count() * penalty_in_minutes


class TestCase(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    standard_in = models.TextField()
    standard_out = models.TextField()
    error_viewable = models.BooleanField()


class Team(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    team_name = models.CharField(max_length=100)
    division = models.CharField(max_length=1, choices=divisions)
    current_contest = models.ForeignKey(Contest, blank=True, null=True)

    def __str__(self):
        return self.team_name + "(" + self.division + ")"

    def get_correct_and_time(self):
        questions_correct = 0
        penalty_time = 0
        submission_time = 0
        for question in Question.objects.filter(contest=self.current_contest, division=self.division):
            num_incorrect_submissions = question.submission_set.filter(correct=False).count()
            penalty_time += num_incorrect_submissions * penalty_in_minutes * 60  # Convert to seconds

            if question.submission_set.filter(correct=True).count() > 0:
                questions_correct += 1
                correct_submission = question.submission_set.filter(correct=True).order_by('submission_time')[0]
                submission_time += \
                    (correct_submission.submission_time - self.current_contest.start_date).total_seconds()
        return questions_correct, (submission_time + penalty_time)


class Submission(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    language = models.CharField(max_length=20, choices=languages)
    code = models.TextField()
    correct = models.BooleanField()
    submission_time = models.DateTimeField()


class StarterCode(models.Model):
    language = models.CharField(max_length=20, choices=languages)
    code = models.TextField()


class Rule(models.Model):
    title = models.CharField(max_length=100)
    body = models.TextField()
