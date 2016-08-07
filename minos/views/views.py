from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from minos.models import Team, Contest, Rule, ClarificationRequest, ClarificationAnswer


def contest_required(function):
    def wrapper(request, *args, **kw):
        team = Team.objects.get(user=request.user)
        if team.current_contest is None:
            messages.error(request, 'A contest selection is required.')
            return redirect('/')
        else:
            return function(request, *args, **kw)
    return wrapper
    
    
@login_required
def index(request):
    team = Team.objects.get(user=request.user)
    contests = Contest.objects.all()
    for contest in contests:
        if not contest.active and contest.start_date < timezone.now():
            contest.closed = True
    return render(request, 'index.html', {
        'current_tab': 'home',
        'contests': contests,
        'selected_contest': team.current_contest
    })


@login_required
def rules(request):
    rules = Rule.objects.all()
    return render(request, 'rules.html', {'current_tab': 'rules', 'rules': rules})


@login_required
@contest_required
def leaderboard(request):
    team = Team.objects.get(user=request.user)
    team_list = Team.objects.filter(division=team.division, current_contest=team.current_contest)
    team_list = rank_current_teams(team_list)

    return render(request, 'leaderboard.html', {
        'current_tab': 'leaderboard',
        'team_list': team_list,
        'team': team,
        'contest': team.current_contest
    })


def rank_current_teams(team_list):
    for team in team_list:
        questions_correct, total_time = team.get_correct_and_time()
        team.questions_correct = questions_correct
        team.total_time_seconds = total_time
        hours = team.total_time_seconds // 3600
        minutes = (team.total_time_seconds % 3600) // 60
        team.total_time = str(int(hours)) + " hours, " + str(int(minutes)) + " minutes"

    # Sort by num questions answered first desc, then by total minutes asc
    team_list = sorted(team_list, key=lambda x: (x.questions_correct, -x.total_time_seconds))[::-1]
    return team_list


@login_required
@contest_required
def clarify(request):
    team = Team.objects.get(user=request.user)
    requests = ClarificationRequest.objects.filter(question__contest=team.current_contest,
                                                   question__division=team.division).order_by('-id')

    return render(request, 'clarify.html', {
        'current_tab': 'clarify',
        'requests': requests,
        'is_admin': request.user.is_superuser
    })


@login_required
@staff_member_required
def add_clarification_answer(request):
    if len(request.GET.get('answer', '')) == 0:
        messages.error(request, 'Missing answer text')
    else:
        answer = ClarificationAnswer(request_id=request.GET['request_id'], body=request.GET['answer'])
        answer.save()
    return redirect('/clarify')


@login_required
@staff_member_required
def add_clarification_request(request, question_id):
    if len(request.GET.get('body', '')) != 0:
        clarify = ClarificationRequest(question_id=question_id, body=request.GET['body'])
        clarify.save()
    return HttpResponse(200)


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
        return redirect('/questions', request=request)
    else:
        return render(request, 'registration/login.html', {'error': 'Invalid username.'})


def logout_view(request):
    logout(request)
    return redirect('/', request=request)
