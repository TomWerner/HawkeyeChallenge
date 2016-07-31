from django.http import StreamingHttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import condition
from django.utils import timezone
import requests
from django.conf import settings
from django.contrib import messages

from minos.models import Question, Team, TestCase, Submission, StarterCode

language_to_id = {
    'ace/mode/python': 0,
    'ace/mode/python-3': 5,
    'ace/mode/c_cpp': 1,
    'ace/mode/java': 2,
    'ace/mode/vbscript': 3,
    'ace/mode/csharp': 4
}


@login_required
def questions(request):
    team = Team.objects.get(user=request.user)
    if team.current_contest is None:
        messages.error(request, "Please select a contest")
        return redirect('/')

    question_list = Question.objects.filter(division=team.division, contest=team.current_contest)
    for question in question_list:
        question.num_submissions = question.get_num_submissions(team)
        question.solved = question.is_solved(team)
        question.penalty = question.get_penalty(team)

    return render(request, 'question/index.html', {
        'current_tab': 'questions',
        'questions': question_list
    })


@login_required
def question_view(request, question_id):
    team = Team.objects.get(user=request.user)
    if team.current_contest is None:
        messages.error(request, "Please select a contest")
        return redirect('/')

    question = get_object_or_404(Question, pk=question_id, contest=team.current_contest)
    code, language = question.get_latest_submissions(team=team)

    return render(request, 'question/question.html', {
        'code': code,
        'language': language,
        'question': question
    })


@login_required
def get_starter_code(request):
    language = request.GET['language']
    return JsonResponse({'code': get_object_or_404(StarterCode, language=language).code})


def fix_output_for_visual_basic(output):
    if 'Compilation successful' in output:
        return output[output.index('Compilation took') + 33:].strip()
    return output


@login_required
def custom_test_case(request):
    r = requests.post(settings.COMPILEBOX_URL + "/compile", json={
        "language": language_to_id[request.POST['language']],
        "code": request.POST['code'],
        "stdin": request.POST['stdin'].replace('\r', '')
    })
    json_data = r.json()
    if request.POST['language'] == 'ace/mode/vbscript':
        json_data['output'] = fix_output_for_visual_basic(json_data['output'])
    return JsonResponse(json_data)


@condition(etag_func=None)
@login_required
def submit_question(request, question_id):
    team = Team.objects.get(user=request.user)
    if team.current_contest is None:
        messages.error(request, "Please select a contest")
        return redirect('/')
    elif not team.current_contest.active:
        def yield_error():
            yield 'data: {"type": "error", "message": "%s"}\n\n' % 'Error! Contest is no longer active.'
        return StreamingHttpResponse(yield_error(), content_type='text/event-stream')

    question = get_object_or_404(Question, pk=question_id)
    return StreamingHttpResponse(stream_submit_question(request, question), content_type='text/event-stream')


def stream_submit_question(request, question):
    team = Team.objects.get(user=request.user)
    test_cases = TestCase.objects.filter(question=question)

    submission_code = request.GET['code']
    submission_language = request.GET['language']

    submission = Submission(team=team,
                            question=question,
                            language=submission_language,
                            code=submission_code,
                            correct=True,
                            submission_time=timezone.now())

    for i, test_case in enumerate(test_cases):
        try:
            r = requests.post(settings.COMPILEBOX_URL + "/compile", json={
                "language": language_to_id[submission.language],
                "code": submission.code,
                "stdin": test_case.standard_in
            })
            json_response = r.json()
        except:
            yield 'data: {"type": "result", "passed": false, "message": "Server error. Contact a judge."}\n\n'
            yield "data: {\"type\": \"done\"}\n\n"
            return

        passed_test_case = False
        message = 'Test Case %d Passed.' % (i + 1)
        errors = json_response['errors']

        if errors is not None and len(errors) > 0:
            message = 'Test Case %d Failed.' % (i + 1)
            if test_case.error_viewable:
                message += '\n\nErrors:\n %s' % errors
        else:
            actual_output = json_response['output'].strip().replace('\r', '')
            if submission_language == 'ace/mode/vbscript':
                actual_output = fix_output_for_visual_basic(actual_output)
            expected_output = test_case.standard_out.strip().replace('\r', '').replace('BLANK', '')
            passed_test_case = actual_output == expected_output
            if not passed_test_case:
                message = 'Test Case %d Failed.' % (i + 1)
                if test_case.error_viewable:
                    message += '\n\nExpected Output:\n%s \n\nActual Output:\n%s' % (expected_output, actual_output)
        if not passed_test_case:
            submission.correct = False

        message = message.replace('\n', '\\n')
        message = message.replace('"', '\\"')
        message = message.replace('/', '\\\\')
        message = message.replace('\r', '')
        passed = str(passed_test_case).lower()  # To javascript boolean

        yield 'data: {"type": "result", "passed": %s, "message": "%s"}\n\n' % (passed, message)
    yield 'data: {"type": "done", "passed": %s}\n\n' % str(submission.correct).lower()

    submission.save()
