import operator

from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import condition
import datetime
from django.utils import timezone
from django.contrib import messages

from minos.models import Question, Team, TestCase, Submission, Contest


# Create your views here.
@login_required
def index(request):
    contests = Contest.objects.all()
    for contest in contests:
        if not contest.active and contest.start_date < timezone.now():
            contest.closed = True
    return render(request, 'index.html', {'current_tab': 'home', 'error': '', 'contests': contests})


@login_required
def rules(request):
    return render(request, 'rules.html', {'current_tab': 'rules'})


@login_required
def leaderboard(request):
    team = Team.objects.get(user=request.user)
    if team.current_contest is None:
        return render(request, 'index.html', {'error': 'Please select a contest.'})

    team_list = Team.objects.filter(division=team.division, current_contest=team.current_contest)

    for x in team_list:
        questions_correct, total_time = x.get_correct_and_time()
        x.questions_correct = questions_correct
        x.total_time_seconds = total_time
        hours = x.total_time_seconds // 3600
        minutes = (x.total_time_seconds % 3600) // 60
        x.total_time = str(int(hours)) + " hours, " + str(int(minutes)) + " minutes"

    # Sort by num questions answered first desc, then by total minutes asc
    team_list = sorted(team_list, key=lambda x: (x.questions_correct, -x.total_time_seconds))[::-1]

    return render(request, 'leaderboard.html', {
        'current_tab': 'leaderboard',
        'team_list': team_list,
        'team': team,
        'contest': team.current_contest
    })


@login_required
def clarify(request):
    return render(request, 'clarify.html', {'current_tab': 'clarify'})


@login_required
def pick_contest(request, contest_id):
    contest = get_object_or_404(Contest, pk=contest_id)
    if not contest.active:
        messages.error(request, str(contest.title) + ' is not active')
        return redirect('/')

    team = Team.objects.get(user=request.user)
    team.current_contest = contest
    team.save()

    return redirect('/questions')


def login_view(request):
    user = authenticate(username=request.POST['username'], use_password=False)
    if user is not None:
        login(request, user)
        return redirect('/', request=request)
    else:
        return render(request, 'registration/login.html', {'error': 'Invalid username.'})


def logout_view(request):
    logout(request)
    return redirect('/', request=request)
