var initArticle = 93, currentArticle;
var sliderValues = [10, 10];

function loadContent(article) {
    $.get("content", {"article": article}, function (data, status, xhr) {
        $("#acontent").html(data.content);
        $("#current").html(data.title);
    });
}

function catchFish(article) {
    $("#pond .fish:not(#current)").remove();
    $.get("catchfish", {"article": article, "sliders": sliderValues},
        function (data, status, xhr) {
            for (var i = 0; i < data.result.length; i++) {
                var fish = data.result[i];
                var div = $("<div>").addClass("fish");
                var id = "fish" + fish.id;
                div.attr("id", id).data("article", fish.id);
                div.attr("title", fish.title).text(fish.title);
                div.click(fishClicked);
                div.appendTo("#pond");
                var translate = "translate(" + fish.dx + "px, " + fish.dy + "px)";
                setTimeout("$('#" + id + "').css('transform', '" + translate + "')", 100);
            }
        }
    );
}

function openArticle(article) {
    currentArticle = article ? article : initArticle;
    for (var i = 0; i < sliderValues.length; i++)
        sliderValues[i] = 10;
    loadContent(currentArticle);
    catchFish(currentArticle);
}

function fishClicked(e) {
    var div = $(this);
    openArticle(div.data("article"));
}

function changeSlider(d, value) {
    sliderValues[d] = value;
    catchFish(currentArticle);
}

$(document).ready(function () {
    openArticle();
});
