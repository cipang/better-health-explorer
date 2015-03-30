var initArticle = 93, currentArticle, pond = new Object();
var sliderValues = [10, 10, 10, 10];

function loadContent(article) {
    $.get("content", {"article": article}, function (data, status, xhr) {
        //$("#acontent").html(data.content);
        $("#current, #pagetitle").html(data.title);
        $("#acontent").empty();
        $("<div>").attr("id", "summary").html(data.summary).appendTo("#acontent");
        var toc = $("<ol>").attr("id", "toc");
        for (var i = 0; i < data.sections.length; i++) {
            var section = data.sections[i];
            var li = $("<li>").appendTo(toc);
            $("<a>").text(section.title).attr("href", "#").data("section", i).addClass("slink").appendTo(li);
            $("<h2>").attr("id", "s" + i).text(section.title).addClass("sheader").appendTo("#acontent");
            $("<div>").addClass("scontent").html(section.content).appendTo("#acontent");
        }
        toc.insertAfter("#summary");
        $("a.slink").click(jumpSection);
    });
}

function jumpSection(e) {
    var section = $(this).data("section");
    var sid = "#s" + section
    location.href = sid;
    $(sid).addClass("highlight");
    setTimeout("$('" + sid + "').removeClass('highlight')", 2000);
    e.preventDefault();
}

function transform(id, dx, dy) {
    var translate = "translate(" + dx + "px, " + dy + "px)";
    setTimeout("$('#" + id + "').css('transform', '" + translate + "')", 100);
}

function remove(id) {
    // setTimeout("$('#" + id + "').css('transform', 'translate(300px,300px)')", 100);
    setTimeout("$('#" + id + "').css('opacity', '0.3')", 100);
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
                    // div.css("width", Math.max(120, fish.similarity / 20 * 180) + "px");
                    // div.css("height", Math.max(50, fish.similarity / 20 * 80) + "px");
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
    $(".slider").slider("value", 10);
    $(".slidervalue").text(10);
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
