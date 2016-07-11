from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from .models import Question, Team


# Create your views here.
@login_required
def index(request):
    return render(request, 'index.html', {'current_tab': 'home'})


@login_required
def rules(request):
    return render(request, 'rules.html', {'current_tab': 'rules'})


@login_required
def questions(request):
    team = Team.objects.get(user=request.user)
    question_list = Question.objects.filter(division=team.division)
    return render(request, 'questions.html', {
        'current_tab': 'questions',
        'questions': question_list
    })


@login_required
def leaderboard(request):
    return render(request, 'leaderboard.html', {'current_tab': 'leaderboard'})


@login_required
def clarify(request):
    return render(request, 'clarify.html', {'current_tab': 'clarify'})


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
