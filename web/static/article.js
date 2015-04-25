var initArticle = 93, currentArticle, pond = new Object();
var sliderValues = [17, 10, 10, 10];
var hoveredFish = null, hoveredObj = null;
var articleOpened = 0;

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
            var n = data.result.length;
            for (var i = 0; i < n; i++)
                if (i < 7 || i == n - 1)
                    console.log("fish" + i, data.result[i].title, data.result[i].score);
        }
    );
}

function openArticle(article, isStated) {
    currentArticle = !article ? initArticle : article;
    if (!isStated) articleOpened++;
    loadContent(currentArticle);
    catchFish(currentArticle);
}

function windowPopStateHandler(e) {
    var state = e.originalEvent.state;
    console.log("popstate", state, state.sliderValues);
    sliderValues = state.sliderValues;
    openArticle(state.article, true);
    updateSlider();
    updateBackForwardButton(state.i > 1, state.i < articleOpened);
}

function updateBackForwardButton(sb, sf) {
    $("#goback").css("visibility", sb ? "visible" : "hidden");
    $("#gofwd").css("visibility", sf ? "visible" : "hidden");
}

function fishClicked() {
    var $obj = $(this);
    var article = $obj.data("article") || $obj.parent().data("article");

    window.history.pushState(getCurrentState());
    console.log("push", getCurrentState(), getCurrentState().sliderValues);
    openArticle(article);
    window.history.pushState(getCurrentState());
    console.log("push", getCurrentState(), getCurrentState().sliderValues);
    fishMouseOut();
    updateBackForwardButton(articleOpened > 1, false);
}

function fishMouseOver() {
    var $obj = $(this);
    var article = $obj.data("article") || $obj.parent().data("article");
    hoveredFish = article;
    hoveredObj = $obj.closest("g");
    hoveredObj.find("rect").attr("fill", "#ffff00");
    setTimeout(tooltipRun, 100);
}

function fishMouseOut() {
    hoveredFish = null;
    if (hoveredObj) {
        hoveredObj.find("rect").attr("fill", "#ffffff");
        hoveredObj = null;
    }
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
            var h1 = pop.find("h1").html(data.title).outerHeight(true);
            var h2 = pop.find("#popsummary").html(data.summary).outerHeight(true);
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

function updateSlider() {
    $(".slider").each(function (index, obj) {
        var sliderID = $(obj).data("dim");
        var v = sliderValues[sliderID];
        $(obj).slider("value", v).parent().find(".slidervalue").text(v);
    });
}

function sliderSlide(e, ui) {
    var slider = $(this);
    var d = parseInt(slider.data("dim"));
    var v = ui.value;
    slider.parent().find(".slidervalue").text(v);
    changeSlider(d, v);
}

function getCurrentState() {
    return {"i": articleOpened, "article": currentArticle,
        "sliderValues": sliderValues.slice()}
}

$(document).ready(function () {
    $(".slider").each(function (index, obj) {
        var sliderID = $(obj).data("dim");
        $(obj).slider({ min: 1, max: 20, value: sliderValues[sliderID], slide: sliderSlide });
    });
    $("#preview").modal();
    $("#previewread").click(previewReadClicked);
    $(window).on("popstate", windowPopStateHandler);
    openArticle();
    window.history.replaceState(getCurrentState());
});
