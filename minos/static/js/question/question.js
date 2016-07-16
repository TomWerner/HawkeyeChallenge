'use strict';

$(document).ready(function () {
    var questionSubmissionForm, languageSelect, codeInput, testCaseResultsList, submitButton, editor;
    var testCaseResultStream;

    var handleTestCaseResult = function (event) {
        var testCaseResult = JSON.parse(event.data);
        if (testCaseResult.type === 'done') {
            testCaseResultStream.close();
            submitButton.html('Submit');
            if (testCaseResult['passed']) {
                testCaseResultsList.empty();
                testResultHtml =
                    '<li><pre class="alert alert-success">All test cases passed!! <a href="/questions">Try another question!</a></pre></li>';
                testCaseResultsList.append(testResultHtml);
            }
        }
        else {
            var testResultHtml;
            if (testCaseResult['passed']) {
                testResultHtml =
                    '<li><pre class="alert alert-success"><strong>Passed!</strong><br>' +
                    testCaseResult['message'] + '</pre></li>'
            }
            else {
                testResultHtml = '<li><pre class="alert alert-danger"><strong>Failed!</strong><br>' +
                    testCaseResult['message'] + '</pre></li>'
            }

            testCaseResultsList.append(testResultHtml);
        }
    };

    var onSubmit = function() {
        var code = editor.getValue().trim();
        codeInput.val(code);
        var questionId = $('#question-id').val();
        $('#language').val(languageSelect.val());

        testCaseResultStream = new EventSource('/question/' + questionId + '/submit' + "?" + questionSubmissionForm.serialize());
        submitButton.html('<span class="glyphicon glyphicon-refresh spinning"></span> Evaluating...');

        testCaseResultsList.empty();
        testCaseResultStream.onmessage = handleTestCaseResult;
    };

    var initPage = function() {
        questionSubmissionForm = $('#questionSubmissionForm');
        languageSelect = $('#languageSelect');
        codeInput = $('#code');
        testCaseResultsList = $('#test-case-results-list');
        submitButton = $('#submit');

        languageSelect.val($('#language').val());

        editor = ace.edit('editor');
        editor.setTheme('ace/theme/monokai');
        editor.getSession().setMode(languageSelect.val());
        editor.setOptions({maxLines: 40});
        editor.setValue(codeInput.val());

        if (editor.session.getLength() <= 40) {
            var content = editor.getValue();
            var newLines = new Array(40 - editor.session.getLength()).join('\n');
            editor.insert(content + newLines);
        }
        editor.setShowPrintMargin(false);
        editor.gotoLine(0);

        languageSelect.on('change', function () {
            editor.getSession().setMode(this.value);
        });

        submitButton.on('click', function (e) {
            e.preventDefault();
            onSubmit();
        });
    };

    initPage();
});