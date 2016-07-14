from django.contrib import admin
from .models import Team, Question, Submission, TestCase


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    fields = ('user', 'team_name', 'division')
    list_display = ('user', 'team_name', 'division')


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    fields = ('title', 'division', 'body')
    list_display = ('title', 'division')


@admin.register(TestCase)
class TestCaseAdmin(admin.ModelAdmin):
    fields = ('question', 'standard_in', 'standard_out', 'error_viewable')
    list_display = fields


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    fields = ('team', 'question', 'language', 'code', 'correct', 'submission_time')
    list_display = ('team', 'question', 'language', 'code', 'correct', 'submission_time')

