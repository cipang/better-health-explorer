var initArticle = 93, currentArticle, pond = new Object();
var sliderValues = [10, 10, 10, 10];
var hoveredFish = null, hoveredObj = null;

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

function fishClicked() {
    var $obj = $(this);
    var article = $obj.data("article") || $obj.parent().data("article");
    /*$.get("summary", {"article": article}, function (data, status, xhr) {
        $("#previewtitle").text(data.title);
        $("#previewcontent").text(data.summary);
    });
    $("#preview").data("article", article).modal("show");*/
    openArticle(article);
    fishMouseOut();
}

function fishMouseOver() {
    var $obj = $(this);
    var article = $obj.data("article") || $obj.parent().data("article");
    hoveredFish = article;
    hoveredObj = $obj.closest("g");
    setTimeout(tooltipRun, 100);
}

function fishMouseOut() {
    hoveredFish = null;
    setTimeout(tooltipRun, 100);
}

function tooltipRun() {
    var pop = $("#hoverpop");
    if (hoveredFish && hoveredFish != pop.data("article")) {
        var offset = hoveredObj.offset();
        var x = offset.left - pop.outerWidth(true) - 5;
        var y = offset.top - $("body").scrollTop();
        pop.data("article", hoveredFish);
        pop.find("h1").text("Please Wait...");
        pop.find("#popsummary").text("");
        pop.css("left", x + "px").css("top", y + "px").fadeIn("fast");

        $.get("summary", {"article": hoveredFish}, function (data, status, xhr) {
            var h1 = pop.find("h1").text(data.title).outerHeight(true);
            var h2 = pop.find("#popsummary").text(data.summary).outerHeight(true);
            pop.css("height", (30 + h1 + h2) + "px");
        });
    } else if (!hoveredFish) {
        pop.removeData("article").fadeOut("fast");
    }
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
