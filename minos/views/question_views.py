from django.http import StreamingHttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import condition
from django.utils import timezone
import requests
from django.conf import settings

from minos.models import Question, Team, TestCase, Submission


@login_required
def questions(request):
    team = Team.objects.get(user=request.user)
    question_list = Question.objects.filter(division=team.division)
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
    question = get_object_or_404(Question, pk=question_id)
    submissions = question.get_submissions(team=team)

    return render(request, 'question/question.html', {
        'code': submissions[0].code,
        'language': submissions[0].language,
        'question': question
    })


@condition(etag_func=None)
@login_required
def submit_question(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return StreamingHttpResponse(stream_submit_question(request, question), content_type='text/event-stream')


def fix_output_for_visual_basic(output):
    if 'Compilation successful' in output:
        return output[output.index('Compilation took') + 33:].strip()
    return output



def stream_submit_question(request, question):
    team = Team.objects.get(user=request.user)
    test_cases = TestCase.objects.filter(question=question)

    submission_code = request.GET['code']
    submission_language = request.GET['language']
    language_to_id = {
        'ace/mode/csharp': 10,
        'ace/mode/c_cpp': 7,
        'ace/mode/clojure': 2,
        'ace/mode/java': 8,
        'ace/mode/golang': 6,
        'ace/mode/javascript': 4,
        'ace/mode/php': 3,
        'ace/mode/python': 0,
        'ace/mode/ruby': 1,
        'ace/mode/scala': 5,
        'ace/mode/vbscript': 9,
        'ace/mode/batchfile': 11,
        'ace/mode/objectivec': 12,
        'ace/mode/mysql': 13,
        'ace/mode/perl': 14
    }

    submission = Submission(team=team,
                            question=question,
                            language=submission_language,
                            code=submission_code,
                            correct=True,
                            submission_time=timezone.now())

    for i, test_case in enumerate(test_cases):
        try:
            r = requests.post(settings.COMPILEBOX_URL + "/compile", data={
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
        print(json_response)

        if errors is not None and len(errors) > 0:
            message = 'Test Case %d Failed.' % (i + 1)
            if test_case.error_viewable:
                message += '\n\nErrors:\n %s' % errors
        else:
            actual_output = json_response['output'].strip().replace('\r', '')
            if submission_language == 'ace/mode/vbscript':
                actual_output = fix_output_for_visual_basic(actual_output)
            expected_output = test_case.standard_out.strip().replace('\r', '')
            passed_test_case = actual_output == expected_output
            if not passed_test_case:
                message = 'Test Case %d Failed.' % (i + 1)
                if test_case.error_viewable:
                    message += '\n\nExpected Output:\n%s \n\nActual Ouput:\n%s' % (expected_output, actual_output)
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
