from django.contrib import admin
from .models import Team, Question, Submission, TestCase, StarterCode, Contest, Rule, ClarificationRequest, \
    ClarificationAnswer


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    fields = ('user', 'team_name', 'division', 'current_contest')
    list_display = ('user', 'team_name', 'division', 'current_contest')


@admin.register(StarterCode)
class StarterCodeAdmin(admin.ModelAdmin):
    fields = ('language', 'code')
    list_display = ('language', 'code')


@admin.register(Rule)
class RuleAdmin(admin.ModelAdmin):
    fields = ('title', 'body')
    list_display = ('title', 'body')


@admin.register(Contest)
class ContestAdmin(admin.ModelAdmin):
    fields = ('title', 'start_date', 'active')
    list_display = ('title', 'start_date', 'active')


class TestCaseInLine(admin.TabularInline):
    model = TestCase
    extra = 2
    fields = ('question', 'standard_in', 'standard_out', 'error_viewable')


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    fields = ('team', 'question', 'language', 'code', 'correct', 'submission_time')
    list_display = ('team', 'question', 'language', 'code', 'correct', 'submission_time')


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    fields = ('contest', 'title', 'division', 'body')
    list_display = ('contest', 'title', 'division', 'test_case_count')

    inlines = [
        TestCaseInLine
    ]

    def test_case_count(self, obj):
        return TestCase.objects.filter(question=obj).count()
