from django.contrib import admin
from .models import Team


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    fields = ('user', 'team_name', 'division')
    list_display = ('user', 'team_name', 'division')
