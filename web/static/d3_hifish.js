var svg;
var round = 0;

function pond_showResult(result) {
    round++;
    var rect = svg.selectAll("rect").data(result, fish_keyFunc);
    rect.enter().
        append("rect").
        attr("x", fish_getX).
        attr("y", 500).
        attr("width", 120).
        attr("height", 50).
        attr("data-article", fish_keyFunc).
        attr("id", function (d) { return d.sid; }).
        attr({"rx": 5, "ry": 5}).
        attr("fill", "#ffffff").
        attr({"stroke": "#000000", "stroke-width": 2});

    rect.transition().duration(1000).
        attr("x", fish_getX).
        attr("y", fish_getY);

    rect.exit().
        transition().duration(1000).
            attr("y", 500).
            remove();

    var text = svg.selectAll("text").data(result, fish_keyFunc);
    text.enter().
        append("text").
        text(fish_getTitle).
        attr("dy", "15").
        attr("x", fish_getX).
        attr("y", 500).
        attr("fill", "red");

    text.transition().duration(1000).
        attr("x", fish_getX).
        attr("y", fish_getY);

    text.exit().remove();
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
    return fish.title;
}

function fish_keyFunc(fish) {
    return fish.id;
}

$(document).ready(function () {
    svg = d3.select("#pond");
});
