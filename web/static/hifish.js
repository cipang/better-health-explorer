var pondTracks = [202.5, 270, 337.5, 45, 90, 135];
var pondMaxItems = 12;
var pondSpaces = new Array(pondTracks.length);
var pondLevels = Math.ceil(pondMaxItems / pondTracks.length);
var pondFishes = {};

for (var i = 0; i < pondSpaces.length; i++) {
    pondSpaces[i] = new Array(pondLevels);
    for (var j = 0; j < pondLevels; j++)
        pondSpaces[i][j] = null;
}

function pond_computeGroup(rank) {
    return Math.trunc(rank / pondTracks.length);
}

function pond_findSpaceForRank(rank) {
    var track;
    var g = pond_computeGroup(rank);
    for (var i = 0; i < pondSpaces.length; i++) {
        if (g < pondSpaces[i].length && !pondSpaces[i][g]) {
            track = i;
            break;
        }
    }
    if (typeof(track) == "undefined")
        throw "Cannot find a track for rank: " + rank;
    return {"track": track, "group": g, "rank": rank};
}

function pond_findExistingFish(fish) {
    for (var track = 0; track < pondSpaces.length; track++)
        for (var group = 0; group < pondLevels; group++)
            if (pondSpaces[track][group])
                if (pondSpaces[track][group] == fish ||
                    pondSpaces[track][group].sid == fish.sid ||
                    pondSpaces[track][group].id == fish.id)
                    return {"track": track, "group": group,
                            "fish": pondSpaces[track][group]}
    return false;
}

function pond_showResult(result) {
    var newFishes = new Array(result.length);
    for (var i = 0; i < result.length; i++)
        newFishes[i] = result[i].sid;
    // Remove expired fishes before moving in new fishes.
    for (var track = 0; track < pondSpaces.length; track++) {
        for (var group = 0; group < pondLevels; group++) {
            var fish = pondSpaces[track][group];
            if (fish && $.inArray(fish.sid, newFishes) == -1) {
                pondSpaces[track][group] = null;
                fish.flag = "D";
                pondFishes[fish.sid] = fish;
            }
        }
    }
    // Add or move fishes with the result list.
    for (var i = result.length - 1; i >= 0; i--) {
        var f = result[i];
        if (pondFishes[f.sid])
            pond_moveFish(f);
        else
            pond_addFish(f);
        newFishes[i] = f.sid;
    }
    pond_draw();
}

function pond_addFish(fish) {
    var addr = pond_findSpaceForRank(fish.rank);
    pondSpaces[addr.track][addr.group] = fish;
    fish.track = addr.track;
    fish.group = addr.group;
    fish.flag = "N";
    pondFishes[fish.sid] = fish;
}

function pond_moveFish(fish) {
    var found = pond_findExistingFish(fish);
    if (!found)
        throw "Attempt to move a fish that does not exist.";
    var newGroup = pond_computeGroup(fish.rank);
    if (found.group != newGroup) {
        pondSpaces[found.track][newGroup] = fish;
        pondSpaces[found.track][found.group] = null;
        fish.group = newGroup;
        fish.flag = "M";
        pondFishes[fish.sid] = fish;
    }
}

function pond_draw() {
    for (var fishSID in pondFishes) {
        var fish = pondFishes[fishSID];
        if (!fish) {
            continue;
        } else if (fish.flag == "D") {
            fish_remove(fishSID);
            delete pondFishes[fishSID];
        } else if (fish.flag == "M") {
            var pos = pond_getLayout(fish);
            fish_transform(fishSID, pos.dx, pos.dy);
            fish.flag = "C";
        } else if (fish.flag == "N") {
            var pos = pond_getLayout(fish);
            fish_add(fish, pos.dx, pos.dy);
            fish.flag = "C";
        }
    }
}

function pond_getLayout(fish) {
    var g = fish.group;
    var l = 80 * (g + 1) + (1 - fish.score) * 100;
    var a = pondTracks[fish.track] * (Math.PI / 180);
    var x = Math.ceil(l * Math.cos(a))
    var y = Math.ceil(l * Math.sin(a))
    return {"dx": x, "dy": y, "length": l}
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
    var translate = "translate(" + dx + "px, " + dy + "px)";
    setTimeout("$('#" + id + "').css('transform', '" + translate + "')", 100);
}

function fish_remove(id) {
    // setTimeout("$('#" + id + "').css('transform', 'translate(300px,300px)')", 100);
    setTimeout("$('#" + id + "').css('opacity', '0.3')", 100);
    setTimeout("$('#" + id + "').remove()", 400);
}
