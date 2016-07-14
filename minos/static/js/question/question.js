'use strict';

$(document).ready(function () {
    var languageSelect = $('#languageSelect');
    languageSelect.val($('#language').val());

    var editor = ace.edit("editor");
    editor.setTheme("ace/theme/monokai");
    editor.getSession().setMode(languageSelect.val());
    editor.setOptions({maxLines: 40});
    editor.setValue($('#code').val());

    if (editor.session.getLength() <= 40) {
        var content = editor.getValue();
        var newLines = new Array(40 - editor.session.getLength()).join("\n");
        editor.insert(content + newLines);
    }
    editor.setShowPrintMargin(false);
    editor.gotoLine(0);

    languageSelect.on('change', function () {
        editor.getSession().setMode(this.value);
    });

    $('#submit').on('click', function () {
        $('#editor-form-submit').val(editor.getValue());
        console.log(editor.getValue());
    });
});