from django.contrib import admin
from .models import Team, Question


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    fields = ('user', 'team_name', 'division')
    list_display = ('user', 'team_name', 'division')


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    fields = ('title', 'division', 'body')
    list_display = ('title', 'division')

