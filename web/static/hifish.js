var pondTracks = [202.5, 270, 337.5, 45, 90, 135];
var pondMaxItems = 12;
var pondSpaces = new Array(pondTracks.length);
var pondLevels = Math.ceil(pondMaxItems / pondTracks.length);
var pondFishNumPerLevel = pondMaxItems / pondLevels;
var pondFishes = {};
var round = 0;

for (var i = 0; i < pondSpaces.length; i++) {
    pondSpaces[i] = new Array(pondLevels);
    for (var j = 0; j < pondLevels; j++)
        pondSpaces[i][j] = null;
}

function allocTable_new() {
    var a = new Array();
    for (var i = 0; i < pondMaxItems; i++)
        a[i] = null;
    return a;
}

function allocTable_find(table, group) {
    var m = group * pondFishNumPerLevel;
    var n = (group + 1) * pondFishNumPerLevel;
    var track = 0;
    for (var i = m; i < n; i++) {
        if (!table[i])
            return {"track": track, "group": group};
        track++;
    }
    console.log("Unable to find a space.", group, table);
    return false;
}

function allocTable_set(table, track, group, value) {
    table[group * pondFishNumPerLevel + track] = value;
    return table;
}

function allocTable_get(table, track, group) {
    return table[group * pondFishNumPerLevel + track];
}

function pond_computeGroup(rank) {
    return Math.trunc(rank / pondTracks.length);
}

function pond_showResult(result) {
    round++;
    var newFishes = {};
    var alloc = allocTable_new();
    for (var i = result.length - 1; i >= 0; i--) {
        var fish = result[i];
        var sid = fish.sid;
        var newGroup = pond_computeGroup(fish.rank);
        if (pondFishes[sid]) {
            var existingFish = pondFishes[sid];
            pond_moveFish(alloc, newFishes, existingFish, fish);
        } else {
            pond_addFish(alloc, newFishes, fish);
        }
    }

    for (var sid in pondFishes) {
        if (!newFishes[sid]) {
            fish_remove(sid);
        }
    }

    pondFishes = newFishes;
    pond_draw();
}

function pond_addFish(table, pond, fish) {
    var pos = allocTable_find(table, pond_computeGroup(fish.rank));
    fish.track = pos.track;
    fish.group = pos.group;
    fish.status = "NEW";
    allocTable_set(table, pos.track, pos.group, fish.sid);
    pond[fish.sid] = fish;
    return fish;
}

function pond_moveFish(table, pond, oldFish, newFish) {
    // Some sanity checks.
    if (!oldFish || !newFish)
        throw "Invalid arguments.";
    if (typeof(oldFish.group) == "undefined")
        throw "An old fish is expected.";

    var newGroup = pond_computeGroup(newFish.rank);
    var pos;
    if (oldFish.group == newGroup) {
        // This fish will stay in its position.
        newFish.status = "STAY";
        pos = {"track": oldFish.track, "group": oldFish.group};
        // Check if that position is occupied.
        if (allocTable_get(table, pos.track, pos.group)) {
            var other = pond[allocTable_get(table, pos.track, pos.group)];
            var pos2 = allocTable_find(table, newGroup);
            other.track = pos2.track;
            other.group = pos2.group;
            allocTable_set(table, pos2.track, pos2.group, other.sid);
        }
    } else {
        newFish.status = "MOVED";
        pos = allocTable_find(table, newGroup);
    }

    newFish.track = pos.track;
    newFish.group = pos.group;
    allocTable_set(table, pos.track, pos.group, newFish.sid);
    pond[newFish.sid] = newFish;
    return newFish;
}

function pond_draw() {
    for (var fishSID in pondFishes) {
        var fish = pondFishes[fishSID];
        if (!fish) {
            continue;
        } else if (fish.status == "MOVED" || fish.status == "STAY") {
            var pos = pond_getLayout(fish);
            fish_transform(fishSID, pos.dx, pos.dy);
            pondFishes[fishSID].draw = round;
        } else if (fish.status == "NEW") {
            var pos = pond_getLayout(fish);
            fish_add(fish, pos.dx, pos.dy);
            pondFishes[fishSID].draw = round;
        }
    }
}

function pond_getLayout(fish) {
    var g = fish.group;
    var t = fish.track;
    var output;

    // var l = 80 * (g + 1) + (1 - fish.score) * 0;
    // var a = pondTracks[fish.track] * (Math.PI / 180);
    // var x = Math.ceil(l * Math.cos(a))
    // var y = Math.ceil(l * Math.sin(a))
    // return {"dx": x, "dy": y, "length": l}

    if (g == 0) {
        switch (t) {
            case 0: output = {"dx": -70, "dy": -60}; break;
            case 1: output = {"dx": 70, "dy": -60}; break;
            case 2: output = {"dx": 125, "dy": 0}; break;
            case 3: output = {"dx": 70, "dy": 60}; break;
            case 4: output = {"dx": -70, "dy": 60}; break;
            case 5: output = {"dx": -125, "dy": 0}; break;
        }
    } else if (g == 1) {
        switch (t) {
            case 0: output = {"dx": 0, "dy": -125}; break;
            case 1: output = {"dx": 125, "dy": -125}; break;
            case 2: output = {"dx": 125, "dy": 125}; break;
            case 3: output = {"dx": 0, "dy": 125}; break;
            case 4: output = {"dx": -125, "dy": 125}; break;
            case 5: output = {"dx": -125, "dy": -125}; break;
        }
    }
    if (!output) {
        console.log("Unable to get layout for: " + fish.sid);
        return {"dx": 0, "dy": 0}
    } else {
        output.dx += Math.random() * 10 - 5
        output.dy += Math.random() * 10 - 5
        return output;
    }
}

function fish_add(fish, dx, dy) {
    var div = $("<div>").addClass("fish");
    div.attr("id", fish.sid).data("article", fish.id);
    div.attr("title", fish.title).text(fish.title);
    div.click(fishClicked);
    // div.css("width", Math.max(120, fish.similarity / 20 * 180) + "px");
    // div.css("height", Math.max(50, fish.similarity / 20 * 80) + "px");
    div.appendTo("#pond");
    fish_transform(fish.sid, dx, dy);
}

function fish_transform(id, dx, dy) {
    if (!document.getElementById(id))
        console.log("Fish not found: " + id);
    var translate = css_makeTranslate(dx, dy);
    var s = "$('#" + id + "').css({'transform': '" + translate + "', "+
        "'opacity': '1'}).data('dx', " + dx + ").data('dy', " + dy + ")";
    setTimeout(s, 100);
}

function css_makeTranslate(x, y) {
    return "translate(" + x + "px, " + y + "px)";
}

function fish_remove(id) {
    var $obj = $("#" + id)
    var dx = $obj.data("dx"), dy = $obj.data("dy");
    if (dx) {
        dy = dy >= 0 ? 200 : -200;
        setTimeout("$('#" + id + "').css('transform', '" +
            css_makeTranslate(dx, dy) + "')", 100);
    }
    setTimeout("$('#" + id + "').css('opacity', '0')", 100);
    // setTimeout("$('#" + id + "').remove()", 850);
    // $("#" + id).remove();
}

function fish_cleanup() {
    var deleted = 0;
    $(".fish").not("#current").each(function (index) {
        var $this = $(this), sid = $this.attr("id");
        if (!pondFishes[sid]) {
            $this.remove();
            deleted++;
        }
    });
    setTimeout(fish_cleanup, 1000);
    // if (deleted > 0)
    //     console.log("fish_cleanup deleted: ", deleted);
}

$(document).ready(function () { fish_cleanup() });
