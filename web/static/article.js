var initArticle = 93, currentArticle, inited = false;
var checkboxValues = [true, true, true, true];
var sliderValues = [19, 10, 10, 10];
var hoveredFish = null, hoveredObj = null;
var articleOpened = 1;

function loadContent(article) {
    $.get("content", {"article": article}, function (data, status, xhr) {
        $("#current, #pagetitle").html(data.title);
        $("#acontent").empty();
        $("<div>").attr("id", "summary").html(data.summary).appendTo("#acontent");
        if (data.sections.length) {
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
        } else {
            $("<div>").html(data.content).insertAfter("#summary");
        }
        handleArticleLinks();
        if ($(window).scrollTop() != 0)
            $("body").ScrollTo();
    });
}

function jumpSection(e) {
    var section = $(this).data("section");
    var sid = "#s" + section
    $(sid).addClass("highlight").ScrollTo({"offsetTop": 35});
    setTimeout("$('" + sid + "').removeClass('highlight')", 2000);
    e.preventDefault();
}

function catchFish(article) {
    $.get("catchfish", {"article": article, "sliders": sliderValues,
            "checkboxes": checkboxValues},
        function (data, status, xhr) {
            pond_showResult(data.result);
            // console.log("*** new fishes ***", new Date());
            // var n = data.result.length;
            // for (var i = 0; i < n; i++)
            //     if (i < 7 || i == n - 1)
            //         console.log("fish" + i, data.result[i].title, data.result[i].score);
        }
    );
}

function openArticle(article, isStated) {
    currentArticle = article;
    if (!isStated)
        articleOpened++;
    loadContent(currentArticle);
    catchFish(currentArticle);
    if (!isStated)
        window.history.pushState(getCurrentState());
    updateBackButtonHint();
}

function windowPopStateHandler(e) {
    var state = e.originalEvent.state;
    checkboxValues = state.checkboxValues;
    sliderValues = state.sliderValues;
    openArticle(state.article, true);
    updateUI();
}

function updateBackButtonHint() {
    if (articleOpened == 2)
        $("#navcontrol em").css("visibility", "visible");
}

function fishClicked() {
    var $obj = $(this);
    var article = $obj.data("article") || $obj.parent().data("article");

    openArticle(article);
    fishMouseOut();
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
        var rect = hoveredObj.find("rect");
        rect.attr("fill", rect.attr("ofill"));
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

function setSlider(d, value) {
    sliderValues[d] = value;
    catchFish(currentArticle);
}

function setCheckbox(d, value) {
    checkboxValues[d] = value;
    catchFish(currentArticle);
}

function updateUI() {
    $(".dim-checkbox").each(function (index, obj) {
        var cbID = $(obj).data("dim");
        var v = checkboxValues[cbID];
        $(obj).prop("checked", v);
    });
    $(".slider").each(function (index, obj) {
        var sliderID = $(obj).data("dim");
        var v = sliderValues[sliderID];
        var cbv = checkboxValues[sliderID];
        var slider = $(obj);
        slider.slider("value", v).parent().find(".slidervalue").text(v);
        slider.slider(cbv ? "enable" : "disable");
    });
}

function sliderSlided(e, ui) {
    var slider = $(this);
    var d = parseInt(slider.data("dim"));
    var v = ui.value;
    slider.parent().find(".slidervalue").text(v);
    setSlider(d, v);
}

function sliderChanged(e, ui) {
    if (inited)
        window.history.replaceState(getCurrentState());
}

function checkboxChanged(e, ui) {
    if (!inited)
        return;

    var cb = $(this);
    var d = parseInt(cb.data("dim"));
    var v = cb.prop("checked");
    var slider = $(".slider[data-dim=" + d + "]");
    slider.slider(v ? "enable" : "disable");

    setCheckbox(d, v);
    window.history.replaceState(getCurrentState());
}

function getCurrentState() {
    var state = {"article": currentArticle,
        "checkboxValues": checkboxValues.slice(),
        "sliderValues": sliderValues.slice()}
    console.log("getCurrentState", state);
    return state;
}

function handleArticleLinks() {
    $("#acontent a").not(".slink").click(articleLinkClicked);
}

function articleLinkClicked(e) {
    e.preventDefault();
    var url = $(this).attr("href");
    $.get("find-article", {"url": url}, function (data, status, xhr) {
        openArticle(data.article);
    }).fail(function () {
        alert("Cannot open this article. It is not provided in this demo.");
    });
}

function statusAnimate(selector, isShow) {
    var filter, options, css;
    if (isShow) {
        filter = ":not(:visible)";
        options = {"start": function () { $(this).show(); }};
        css = {"top": 1};
    } else {
        filter = ":visible";
        options = {"done": function () { $(this).hide(); }};
        css = {"top": -35};
    }
    $(selector).filter(".status").filter(filter).animate(css, options);
}

$(document).ready(function () {
    // Sliders.
    var $slider = $(".slider");
    $slider.slider({ min: 1, max: 20, value: 1, range: "min",
        slide: sliderSlided, change: sliderChanged });

    // Slider: Handle move one step when click on the bar.
    var clickOnBar = false;
    $slider.on("slidestart", function (event, ui) {
        if (!clickOnBar) {
            $(this).slider("value", ui.value + 1);
            sliderSlided.call($(this), null, {"value": ui.value + 1});
            return false;
        } else {
            clickOnBar = false;
        }
    });
    $(".slider .ui-slider-range").mousedown(function () {
        var slider = $(this).parent();
        var v = slider.slider("value") - 1;
        slider.slider("value", v);
        sliderSlided.call(slider, null, {"value": v});
        return false;
    });
    $(".slider .ui-slider-handle").mousedown(function () { clickOnBar = true; }).unbind("keydown");
    $(".slider").css("background", $(".slider .ui-slider-range").css("background"));

    // Checkboxes.
    $(".dim-checkbox").change(checkboxChanged);
    updateUI();

    // History and states.
    $(window).on("popstate", windowPopStateHandler);

    // Scrolling.
    $(window).on("scroll", function () {
        if ($(window).scrollTop() > 0)
            statusAnimate("#topbutton", true);
        else
            statusAnimate("#topbutton", false);
    });
    $("#topbutton a").click(function (e) {
        e.preventDefault();
        $("body").ScrollTo();
    });

    // AJAX status.
    var lastLoadTimeout = 0;
    $(document).ajaxStart(function () {
        lastLoadTimeout = setTimeout('statusAnimate("#ajaxloading", true)', 500);
    });
    $(document).ajaxStop(function () {
        clearTimeout(lastLoadTimeout);
        statusAnimate("#ajaxloading", false);
    });

    inited = true;
    openArticle(initArticle, true);
    window.history.replaceState(getCurrentState());
});
