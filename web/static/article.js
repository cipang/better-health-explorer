var initArticle = 93;

function openArticle(article) {
    $.get("content/", {"article": article}, function (data, status, xhr) {
        $("#acontent").html(data.content);
        $("#current").html(data.title);
    });
}

function center(article) {

}

$(document).ready(function () {
    openArticle(initArticle);
    center(initArticle);
});
