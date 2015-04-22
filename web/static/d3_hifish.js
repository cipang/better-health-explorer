var svg;
var round = 0;

function pond_showResult(result) {
    round++;
    var g = svg.selectAll("g").data(result, fish_keyFunc);
    var enter = g.enter().append("g").
        attr("transform", function (d) { return "translate(" + fish_getX(d) + ",500)" }).
        attr("data-article", fish_keyFunc).
        attr("id", function (d) { return d.sid; }).
        attr("data-article", fish_keyFunc);

    enter.append("rect").
        attr({"rx": 5, "ry": 5, "x": 0, "y": 0}).
        attr("width", 120).
        attr("height", 50).
        attr("fill", "#ffffff").
        attr({"stroke": "#000000", "stroke-width": 2}).
        on("click", fishClicked).
        on("mouseover", fishMouseOver).
        on("mouseout", fishMouseOut);

    enter.append("text").
        text(fish_getTitle).
        attr({"x": 10, "y": 5, "dx": 0, "dy": "1em"}).
        attr({"width": 120, "height": 50}).
        call(wrap, 100).
        on("click", fishClicked).
        on("mouseover", fishMouseOver).
        on("mouseout", fishMouseOut);

    g.transition().duration(1000).
        attr("transform", function (d) { return "translate(" + fish_getX(d) +
            "," + fish_getY(d) + ")" });

    g.exit().
        transition().duration(1000).
            attr("transform", function (d) { return "translate(" + fish_getX(d) +
                ",500)" }).
            remove();
}

function pond_computeGroup(rank) {
    return Math.trunc(rank / 3);
}

function pond_computeTrack(rank) {
    return rank % 3;
}

function fish_getX(fish) {
    var track = pond_computeTrack(fish.rank);
    return 120 * track + 5 * track + 5;
}

function fish_getY(fish) {
    var group = pond_computeGroup(fish.rank);
    return 50 * group + 10 * group + 10;
}

function fish_getTitle(fish) {
    return fish.title + "\n" + (fish.score * 100).toPrecision(4);
}

function fish_keyFunc(fish) {
    return fish.id;
}

function wrap(text, width) {
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
