var initArticle = 93, currentArticle, pond = new Object();
var sliderValues = [10, 10, 10, 10];

function loadContent(article) {
    $.get("content", {"article": article}, function (data, status, xhr) {
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

function catchFish(article) {
    $.get("catchfish", {"article": article, "sliders": sliderValues},
        function (data, status, xhr) {
            pond_showResult(data.result);
        }
    );
}

function openArticle(article) {
    if (!currentArticle) {
        for (var i = 0; i < sliderValues.length; i++)
            sliderValues[i] = 10;
        $(".slider").slider("value", 10);
        $(".slidervalue").text(10);
    }
    currentArticle = article ? article : initArticle;
    loadContent(currentArticle);
    catchFish(currentArticle);
}

function fishClicked(e) {
    var $div = $(this);
    var article = $div.data("article");
    $("#previewtitle").text($div.text());
    $.get("summary", {"article": article}, function (data, status, xhr) {
        $("#previewtitle").text(data.title);
        $("#previewcontent").text(data.summary);
    });
    $("#preview").data("article", article).modal("show");
}

function previewReadClicked(e) {
    openArticle($("#preview").modal("hide").data("article"));
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
    $("#preview").modal();
    $("#previewread").click(previewReadClicked);
    openArticle();
});
