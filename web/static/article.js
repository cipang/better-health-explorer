var initArticle = 93, currentArticle, pond = new Object();
var sliderValues = [10, 10];

function loadContent(article) {
    $.get("content", {"article": article}, function (data, status, xhr) {
        $("#acontent").html(data.content);
        $("#current").html(data.title);
    });
}

function transform(id, dx, dy) {
    var translate = "translate(" + dx + "px, " + dy + "px)";
    setTimeout("$('#" + id + "').css('transform', '" + translate + "')", 100);
}

function remove(id) {
    setTimeout("$('#" + id + "').css('transform', 'translate(300px,300px)')", 100);
    setTimeout("$('#" + id + "').remove()", 400);
}

function catchFish(article) {
    $.get("catchfish", {"article": article, "sliders": sliderValues},
        function (data, status, xhr) {
            var result = data.result;
            for (var id in result) {
                var fish = result[id];
                if (!pond[id]) {
                    var div = $("<div>").addClass("fish");
                    div.attr("id", id).data("article", fish.id);
                    div.attr("title", fish.title).text(fish.title);
                    div.click(fishClicked);
                    div.appendTo("#pond");
                }
                transform(id, fish.dx, fish.dy);
            }
            for (var id in pond) {
                if (!result[id])
                    remove(id);
            }
            pond = result;
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

function sliderSlide(e, ui) {
    var slider = $(this);
    var d = parseInt(slider.data("dim"));
    var v = ui.value;
    slider.parent().find(".slidervalue").text(v);
    changeSlider(d, v);
}

$(document).ready(function () {
    $(".slider").slider({ min: 1, max: 20, value: 10, slide: sliderSlide });
    openArticle();
});
