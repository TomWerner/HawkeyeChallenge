import datetime

from django.contrib.auth.models import User
from django.test import TestCase
from minos.models import Contest, Question, Submission, Team, divisions, languages, penalty_in_minutes
from django.utils import timezone

from minos.views import views

minutes_to_seconds = 60


class MockTeam:
    def __init__(self, questions_correct, total_time, name):
        self.questions_correct = questions_correct
        self.total_time = total_time
        self.name = name

    # Actual function tested in test/models/test_team.py
    def get_correct_and_time(self):
        return self.questions_correct, self.total_time

    def __str__(self):
        return str(self.__dict__)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


class LeaderboardTestCase(TestCase):
    def setUp(self):
        pass

    def rank_by_team_name(self, team_list):
        return sorted(team_list, key=lambda x: x.name)

    def test_rank_current_teams_only_questions(self):
        team_list = [MockTeam(1, 0, 'C'), MockTeam(5, 0, 'A'), MockTeam(3, 0, 'B')]
        ranked_teams = views.rank_current_teams(team_list)

        self.assertEquals(ranked_teams, self.rank_by_team_name(team_list))
        self.assertEqual(ranked_teams[0].name, 'A')

    def test_rank_current_teams_only_time(self):
        team_list = [MockTeam(0, 100, 'C'), MockTeam(0, 3, 'A'), MockTeam(0, 44, 'B')]
        ranked_teams = views.rank_current_teams(team_list)

        self.assertEquals(ranked_teams, self.rank_by_team_name(team_list))
        self.assertEqual(ranked_teams[0].name, 'A')

    def test_rank_current_teams_both(self):
        # Rank first based off of most questions correct. If two teams have the same number correct,
        # the team with the lowest time should be first
        five_question_teams = [MockTeam(5, 100, 'C'), MockTeam(5, 3, 'A'), MockTeam(5, 44, 'B')]
        three_question_teams = [MockTeam(3, 0, 'D'), MockTeam(3, 1000, 'E')]
        one_question_teams = [MockTeam(1, -100, 'F')]
        zero_question_teams = [MockTeam(0, -10000, 'G')]
        team_list = zero_question_teams + one_question_teams + three_question_teams + five_question_teams

        ranked_teams = views.rank_current_teams(team_list)

        self.assertEquals(ranked_teams, self.rank_by_team_name(team_list))
        self.assertEqual(ranked_teams[0].name, 'A')