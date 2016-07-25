'use strict';

$(document).ready(function () {
    var questionSubmissionForm, languageSelect, codeInput, testCaseResultsList, submitButton, editor,
        customSubmitButton;
    var testCaseResultStream;

    var handleTestCaseResult = function (event) {
        var testCaseResult = JSON.parse(event.data);
        if (testCaseResult.type === 'done') {
            testCaseResultStream.close();
            submitButton.html('Submit');
            submitButton.attr('disabled', false);
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

    var onSubmit = function () {
        var code = editor.getValue().trim();
        codeInput.val(code);
        var questionId = $('#question-id').val();
        var languageString = languageSelect.val().toString();
        $('#language').val(languageString);

        testCaseResultStream = new EventSource('/question/' + questionId + '/submit' + "?" + questionSubmissionForm.serialize());
        submitButton.html('<span class="glyphicon glyphicon-refresh spinning"></span> Evaluating...');
        submitButton.attr('disabled', true);

        testCaseResultsList.empty();
        testCaseResultStream.onmessage = handleTestCaseResult;
    };

    var fixPython3 = function (languageString) {
        if (languageString.indexOf('-') > 0) {
            languageString = languageString.substring(0, languageString.indexOf('-'))
        }
        return languageString;
    };

    var initPage = function () {
        questionSubmissionForm = $('#questionSubmissionForm');
        languageSelect = $('#languageSelect');
        codeInput = $('#code');
        testCaseResultsList = $('#test-case-results-list');
        submitButton = $('#submit');
        customSubmitButton = $('#submit-custom');

        languageSelect.val($('#language').val());

        editor = ace.edit('editor');
        editor.setTheme('ace/theme/monokai');
        editor.getSession().setMode(fixPython3(languageSelect.val()));
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
            editor.getSession().setMode(fixPython3(this.value));
        });

        submitButton.on('click', function (e) {
            e.preventDefault();
            onSubmit();
        });

        customSubmitButton.on('click', function (e) {
            e.preventDefault();

            var code = editor.getValue().trim();
                var languageIdLookup = {
                    'ace/mode/java': 2,
                    'ace/mode/python': 0,
                    'ace/mode/python-3': 5,
                    'ace/mode/vbscript': 3,
                    'ace/mode/c_cpp': 1,
                    'ace/mode/csharp': 4
                };

                $.ajax({
                    type: "POST",
                    url: '/compile',
                    data: JSON.stringify({
                        'language': languageIdLookup[languageSelect.val()],
                        'code': code,
                        'stdin': $('#stdin').val()
                    }),
                    success: function (e) {
                        submitButton.html('Submit');
                        submitButton.attr('disabled', false);
                        $('#stdout').val(e['output']);
                        $('#stderr').val(e['errors']);
                    },
                    dataType: 'json'
                });
                submitButton.html('<span class="glyphicon glyphicon-refresh spinning"></span> Evaluating...');
                submitButton.attr('disabled', true);
        })
    };

    initPage();
});