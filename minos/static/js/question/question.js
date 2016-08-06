'use strict';

$(document).ready(function () {
    // using jQuery
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    $.ajaxSetup({
        headers: {"X-CSRFToken": getCookie("csrftoken")}
    });

    var questionSubmissionForm, languageSelect, codeInput, testCaseResultsList, submitButton, editor,
        customSubmitButton, modalEditor, useStarterCodeButton, questionSpinner, testCaseResultsHeader,
        clarifyRequest;
    var testCaseResultStream;

    var finishSubmission = function() {
        questionSpinner.hide();
    };

    var startSubmission = function() {
        questionSpinner.show();
        testCaseResultsHeader.show();
    };

    var handleTestCaseResult = function (event) {
        var testCaseResult = JSON.parse(event.data);
        if (testCaseResult.type === 'done') {
            testCaseResultStream.close();
            submitButton.html('Submit');
            submitButton.attr('disabled', false);
            if (testCaseResult['passed']) {
                testResultHtml =
                    '<li><pre class="alert alert-success">All test cases passed!! <a href="/questions">Try another question!</a></pre></li>';
                testCaseResultsList.append(testResultHtml);
            }
            finishSubmission();
        }
        else if (testCaseResult.type === 'error') {
            testCaseResultStream.close();
            submitButton.html('Submit');
            submitButton.attr('disabled', false);
            alert(testCaseResult['message']);
            finishSubmission();
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
        if (!confirm("Incorrect submissions have a 10 minute time penalty. Do you wish to submit a solution?")) {
            return;
        }
        startSubmission();
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

    var showStarterCodeModal = function () {
        var selectedLanguage = languageSelect.val();
        var languageText = $('[value="' + selectedLanguage + '"]').text();
        $('#starter-code-modal-title').text('Use ' + languageText + ' Starter Code?');
        $.get('/starterCode?language=' + encodeURIComponent(selectedLanguage))
            .success(function (e) {
                modalEditor = ace.edit('modalEditor');
                modalEditor.$blockScrolling = Infinity;
                modalEditor.setTheme('ace/theme/monokai');
                modalEditor.getSession().setMode(fixPython3(languageSelect.val()));
                modalEditor.setOptions({maxLines: 40});
                modalEditor.setValue(e['code']);
                modalEditor.setReadOnly(true);
                modalEditor.gotoLine(0);
            });
        $('#starter-code-modal').modal('show');
    };

    var showClarificationRequestModal = function() {
        $('#clarification-modal').modal('show');
    };

    var setEditorValue = function (newEditorValue) {
        editor.setValue(newEditorValue);

        if (editor.session.getLength() <= 40) {
            var content = editor.getValue();
            var newLines = new Array(40 - editor.session.getLength()).join('\n');
            editor.insert(content + newLines);
        }
        editor.gotoLine(0);
    };

    var initPage = function () {
        questionSubmissionForm = $('#questionSubmissionForm');
        languageSelect = $('#languageSelect');
        codeInput = $('#code');
        testCaseResultsList = $('#test-case-results-list');
        submitButton = $('#submit');
        customSubmitButton = $('#submit-custom');
        useStarterCodeButton = $('#use-starter-code');
        questionSpinner = $('#question-spinner');
        testCaseResultsHeader = $('#test-case-results-header');
        clarifyRequest = $('#clarify-request');

        questionSpinner.hide();
        testCaseResultsHeader.hide();

        languageSelect.val($('#language').val());

        editor = ace.edit('editor');
        editor.$blockScrolling = Infinity;
        editor.setTheme('ace/theme/monokai');
        editor.getSession().setMode(fixPython3(languageSelect.val()));
        editor.setOptions({maxLines: 40});
        setEditorValue(codeInput.val());
        if (codeInput.val().length === 0) {
            showStarterCodeModal();
        }
        editor.setShowPrintMargin(false);

        languageSelect.on('change', function () {
            editor.getSession().setMode(fixPython3(this.value));
            showStarterCodeModal();
        });

        submitButton.on('click', function (e) {
            e.preventDefault();
            onSubmit();
        });

        useStarterCodeButton.on('click', function () {
            setEditorValue(modalEditor.getValue());
        });

        clarifyRequest.on('click', function(e) {
            showClarificationRequestModal();
        });

        customSubmitButton.on('click', function (e) {
            e.preventDefault();
            var code = editor.getValue().trim();

            $.ajax({
                type: "POST",
                url: '/customTestCase',
                data: {
                    'language': languageSelect.val(),
                    'code': code,
                    'stdin': $('#stdin').val()
                },
                success: function (e) {
                    customSubmitButton.html('Custom Input');
                    customSubmitButton.attr('disabled', false);
                    $('#stdout').val(e['output']);
                    $('#stderr').val(e['errors']);
                },
                dataType: 'json'
            });
            customSubmitButton.html('<span class="glyphicon glyphicon-refresh spinning"></span> Evaluating...');
            customSubmitButton.attr('disabled', true);
        });
    };

    var converter = new Markdown.Converter();
    var questions = $('.question-body-input');
    var questionBodies = $('.question-body');
    for (var i = 0; i < questions.length; i++) {
        var questionMarkdown = $(questions[i]).val();
        var questionHTML = converter.makeHtml(questionMarkdown);
        $(questionBodies[i]).html(questionHTML);
    }

    initPage();
});