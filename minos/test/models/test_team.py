import datetime

from django.contrib.auth.models import User
from django.test import TestCase
from minos.models import Contest, Question, Submission, Team, divisions, languages, penalty_in_minutes
from django.utils import timezone

minutes_to_seconds = 60


class TeamTestCase(TestCase):
    def setUp(self):
        self.contest = Contest.objects.create(title="Contest 1", start_date=timezone.now(), active=True)
        self.question_1 = Question.objects.create(title="Question 1", division=divisions[0],
                                body="Question text", contest=self.contest)
        self.question_2 = Question.objects.create(title="Question 1", division=divisions[0],
                                                  body="Question text", contest=self.contest)
        self.question_3 = Question.objects.create(title="Question 1", division=divisions[0],
                                                  body="Question text", contest=self.contest)

        self.user_1 = User.objects.create_user('team_1')
        self.user_2 = User.objects.create_user('team_2')
        self.team_1 = Team.objects.create(user=self.user_1, division=divisions[0],
                                          current_contest=self.contest, team_name="Team 1")
        self.team_2 = Team.objects.create(user=self.user_2, division=divisions[0],
                                          current_contest=self.contest, team_name="Team 2")

    @staticmethod
    def create_submission(team, correct, question, delay=0):
        Submission.objects.create(team=team,
                                  question=question,
                                  language=languages[0][0],
                                  code='', correct=correct,
                                  submission_time=timezone.now() + datetime.timedelta(minutes=delay))

    def test_get_correct_and_time_simple(self):
        self.create_submission(self.team_1, True, self.question_1, delay=5)

        correct, time = self.team_1.get_correct_and_time()
        self.assertEquals(correct, 1)
        self.assertEquals(int(time), 5 * minutes_to_seconds)  # 5 minutes

    def test_get_correct_and_time_simple_with_penalty(self):
        self.create_submission(self.team_1, False, self.question_1, delay=3)
        self.create_submission(self.team_1, True, self.question_1, delay=5)

        correct, time = self.team_1.get_correct_and_time()
        self.assertEquals(correct, 1)
        self.assertEquals(int(time), (5 + penalty_in_minutes) * minutes_to_seconds)  # 5 minutes + penalty

    def test_get_correct_with_penalty_and_no_correct(self):
        self.create_submission(self.team_1, False, self.question_1, delay=3)

        correct, time = self.team_1.get_correct_and_time()
        self.assertEquals(correct, 0)
        self.assertEquals(int(time), penalty_in_minutes * minutes_to_seconds)

    def test_get_correct_multiple_questions(self):
        self.create_submission(self.team_1, False, self.question_1, delay=3)
        self.create_submission(self.team_1, True, self.question_1, delay=5)
        question_1_penalty = 1 * penalty_in_minutes * minutes_to_seconds
        question_1_time = 5 * minutes_to_seconds

        self.create_submission(self.team_1, False, self.question_2, delay=1)
        self.create_submission(self.team_1, False, self.question_2, delay=2)
        self.create_submission(self.team_1, False, self.question_2, delay=3)
        self.create_submission(self.team_1, True, self.question_2, delay=12)
        question_2_penalty = 3 * penalty_in_minutes * minutes_to_seconds
        question_2_time = 12 * minutes_to_seconds

        self.create_submission(self.team_1, False, self.question_3, delay=20)
        question_3_time = 20 * minutes_to_seconds

        self.create_submission(self.team_2, False, self.question_3, delay=20)

        correct, time = self.team_1.get_correct_and_time()
        self.assertEquals(correct, 2)
        self.assertEquals(int(time), (question_1_penalty + question_1_time +
                                      question_2_penalty + question_2_time +
                                      question_3_time))
