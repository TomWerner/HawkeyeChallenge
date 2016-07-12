'use strict';

$( document ).ready(function() {
    var converter = new Markdown.Converter();
    var questions = $('.question-body-input');
    var questionBodies = $('.question-body');
    for (var i = 0; i < questions.length; i++) {
        var questionMarkdown = $(questions[i]).val();
        var questionHTML = converter.makeHtml(questionMarkdown);
        $(questionBodies[i]).html(questionHTML);
    }
    console.log(questions);
});