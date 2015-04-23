var svg;
var round = 0;
var fishWidth = [120, 120, 20];
var fishHeight = [100, 50, 20];
var cx = 0, cy = 5;

function pond_showResult(result) {
    round++;    // Check how many calls to server only.

    // Calculate fish positions and sizes.
    var cx = 5, cy = 5, lastTier = 0, rowHeight = 0;
    var nextRow = function () {
        cx = 5;
        cy += rowHeight + 5;
        rowHeight = 0;
    };

    for (i in result) {
        var fish = result[i];
        if (lastTier != fish.tier && cx != 5) nextRow();

        fish._width = fishWidth[fish.tier];
        fish._height = fishHeight[fish.tier];
        fish._x = cx;
        fish._y = cy;

        rowHeight = Math.max(rowHeight, fish._height);
        lastTier = fish.tier;
        cx += fish._width + 5;
        if (cx >= 360) nextRow();
    }

    var g = svg.selectAll("g").data(result, fish_keyFunc);
    var enter = g.enter().append("g").
        attr("transform", function (d) { return "translate(" + fish_getX(d) + ",500)" }).
        attr("data-article", fish_keyFunc).
        attr("id", function (d) { return d.sid; }).
        attr("data-article", fish_keyFunc).
        attr("data-score", function (d) { return (d.score * 100).toPrecision(4); });

    enter.append("rect").
        attr({"rx": 5, "ry": 5, "x": 0, "y": 0}).
        attr("width", fish_getWidth).
        attr("height", fish_getHeight).
        attr("fill", "#ffffff").
        attr({"stroke": "#ccc", "stroke-width": 1}).
        on("click", fishClicked).
        on("mouseover", fishMouseOver).
        on("mouseout", fishMouseOut);

    enter.append("text").
        attr({"x": 10, "y": 5, "dx": 0, "dy": "1em"}).
        on("click", fishClicked).
        on("mouseover", fishMouseOver).
        on("mouseout", fishMouseOut);

    var update = g.transition().duration(1000).delay(fish_getDelay).
        attr("transform", function (d) { return "translate(" + fish_getX(d) +
            "," + fish_getY(d) + ")" });

    update.select("rect").
        attr("width", fish_getWidth).
        attr("height", fish_getHeight);

    update.select("text").
        attr("opacity", fish_getOpacity);

    g.select("text").
        text(fish_getTitle).
        attr("width", function (d) { return fish_getWidth(d) - 20; }).
        call(wrap);

    g.exit().
        transition().duration(1000).
            attr("transform", function (d) { return "translate(" + fish_getX(d) +
                ",500)" }).
            remove();
}

function pond_computeGroup(order) {
    return Math.trunc(order / 3);
}

function pond_computeTrack(order) {
    return order % 3;
}

function fish_getDelay(fish) {
    return fish.order * 20;
}

function fish_getOpacity(fish) {
    return fish.tier <= 1 ? 1.0 : 0.0;
}

function fish_getX(fish) {
    // var track = pond_computeTrack(fish.order);
    // return 120 * track + 5 * track + 5;
    return fish._x;
}

function fish_getY(fish) {
    // var group = pond_computeGroup(fish.order);
    // return 50 * group + 10 * group + 10;
    return fish._y;
}

function fish_getWidth(fish) {
    return fish._width;
}

function fish_getHeight(fish) {
    return fish._height;
}

function fish_getTitle(fish) {
    return fish.tier <= 1 ? fish.title : "";
}

function fish_keyFunc(fish) {
    return fish.id;
}

function wrap(text) {
    text.each(function() {
        var text = d3.select(this),
                words = text.text().split(/\s+/).reverse(),
                word,
                line = [],
                lineNumber = 0,
                lineHeight = 1.125, // ems
                x = text.attr("x"),
                y = text.attr("y"),
                dy = parseFloat(text.attr("dy")),
                width = text.attr("width"),
                tspan = text.text(null).append("tspan").attr("x", x).attr("y", y).attr("dy", dy + "em");
        while (word = words.pop()) {
            line.push(word);
            tspan.text(line.join(" "));
            if (tspan.node().getComputedTextLength() > width) {
                line.pop();
                tspan.text(line.join(" "));
                line = [word];
                tspan = text.append("tspan").attr("x", x).attr("y", y).attr("dy", ++lineNumber * lineHeight + dy + "em").text(word);
            }
        }
    });
}

$(document).ready(function () {
    svg = d3.select("#pond");
});
