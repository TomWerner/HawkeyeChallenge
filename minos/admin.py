from django.contrib import admin
from .models import Team, Question, Submission, TestCase


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    fields = ('user', 'team_name', 'division')
    list_display = ('user', 'team_name', 'division')


class TestCaseInLine(admin.TabularInline):
    model = TestCase
    extra = 2
    fields = ('question', 'standard_in', 'standard_out', 'error_viewable')


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    fields = ('title', 'division', 'body')
    list_display = ('title', 'division', 'test_case_count')

    inlines = [
        TestCaseInLine
    ]

    def test_case_count(self, obj):
        return TestCase.objects.filter(question=obj).count()


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    fields = ('team', 'question', 'language', 'code', 'correct', 'submission_time')
    list_display = ('team', 'question', 'language', 'code', 'correct', 'submission_time')

