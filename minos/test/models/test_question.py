import datetime

from django.contrib.auth.models import User
from django.test import TestCase
from minos.models import Contest, Question, Submission, Team, divisions, languages, penalty_in_minutes
from django.utils import timezone


class QuestionTestCase(TestCase):
    def setUp(self):
        self.contest = Contest.objects.create(title="Contest 1", start_date=timezone.now(), active=True)
        self.question = Question.objects.create(title="Question 1", division=divisions[0],
                                body="Question text", contest=self.contest)
        self.user_1 = User.objects.create_user('team_1')
        self.user_2 = User.objects.create_user('team_2')
        self.team_1 = Team.objects.create(user=self.user_1, division=divisions[0],
                                          current_contest=self.contest, team_name="Team 1")
        self.team_2 = Team.objects.create(user=self.user_2, division=divisions[0],
                                          current_contest=self.contest, team_name="Team 2")

    def create_submission(self, team, correct, code='', language_index=0, delay=0):
        Submission.objects.create(team=team, question=self.question, language=languages[language_index][0],
                                  code=code, correct=correct,
                                  submission_time=timezone.now() + datetime.timedelta(minutes=delay))

    def test_is_solved_no_submissions(self):
        self.assertFalse(self.question.is_solved(self.team_1))
        self.assertFalse(self.question.is_solved(self.team_2))

    def test_is_solved_incorrect_submissions(self):
        self.create_submission(self.team_1, False)
        self.create_submission(self.team_2, False)
        self.create_submission(self.team_2, False)

        self.assertFalse(self.question.is_solved(self.team_1))
        self.assertFalse(self.question.is_solved(self.team_2))

    def test_is_solved_correct_submissions(self):
        self.create_submission(self.team_1, True)
        self.create_submission(self.team_2, False)

        self.assertTrue(self.question.is_solved(self.team_1))
        self.assertFalse(self.question.is_solved(self.team_2))

    def test_get_num_submissions(self):
        self.assertEquals(self.question.get_num_submissions(self.team_1), 0)
        self.assertEquals(self.question.get_num_submissions(self.team_2), 0)

        self.create_submission(self.team_1, True)
        self.create_submission(self.team_1, True)

        self.assertEquals(self.question.get_num_submissions(self.team_1), 2)
        self.assertEquals(self.question.get_num_submissions(self.team_2), 0)

    def test_get_penalty(self):
        self.assertEquals(self.question.get_penalty(self.team_1), 0)
        self.assertEquals(self.question.get_penalty(self.team_2), 0)

        self.create_submission(self.team_1, False)
        self.create_submission(self.team_1, False)
        self.create_submission(self.team_1, True)

        self.assertEquals(self.question.get_penalty(self.team_1), penalty_in_minutes * 2)
        self.assertEquals(self.question.get_penalty(self.team_2), 0)

    def test_get_latest_submission_no_submissions(self):
        code, language = self.question.get_latest_submission(self.team_1)
        self.assertEquals(code, '')
        self.assertEquals(language, 'ace/mode/python-3')

        code, language = self.question.get_latest_submission(self.team_2)
        self.assertEquals(code, '')
        self.assertEquals(language, 'ace/mode/python-3')

    def test_get_latest_submission_single_submission(self):
        self.create_submission(self.team_1, False, 'code', 1)

        code, language = self.question.get_latest_submission(self.team_1)
        self.assertEquals(code, 'code')
        self.assertEquals(language, languages[1][0])

        code, language = self.question.get_latest_submission(self.team_2)
        self.assertEquals(code, '')
        self.assertEquals(language, 'ace/mode/python-3')

    def test_get_latest_submission_multiple_submission(self):
        self.create_submission(self.team_1, False, 'code', 1)
        self.create_submission(self.team_1, False, 'code 2', 1, delay=5)

        code, language = self.question.get_latest_submission(self.team_1)
        self.assertEquals(code, 'code 2')
        self.assertEquals(language, languages[1][0])

        code, language = self.question.get_latest_submission(self.team_2)
        self.assertEquals(code, '')
        self.assertEquals(language, 'ace/mode/python-3')




