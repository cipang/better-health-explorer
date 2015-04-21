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
        on("click", fishClicked);

    enter.append("text").
        text(fish_getTitle).
        attr({"x": 0, "y": 0, "dx": 7, "dy": 17});

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
    return fish.title + "\n" + fish.score;
}

function fish_keyFunc(fish) {
    return fish.id;
}

$(document).ready(function () {
    svg = d3.select("#pond");
});
