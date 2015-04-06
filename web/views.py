from django.shortcuts import render
from django.http import Http404, JsonResponse
from extract.models import Article
from web.models import *
from web.overlapremoval import Rectangle, remove_overlap
from random import randint
from collections import namedtuple
import math
import sys


Point = namedtuple("Point", ["x", "y"])
CENTER = Point(130, 160)
SLIDER_MIN = 1
SLIDER_MAX = 20
CENTER_DISTANCE_MIN = 100

ALL_SIM = None


class FishRect(Rectangle):

    """Displayed rectangle of each fish. For overlap removal."""

    def __init__(self, x, y, width, height, fish_id):
        super(FishRect, self).__init__(x, y, width, height)
        self.fish_id = fish_id


def home(request):
    return render(request, "home.html",
                  {"loop": range(0, 20),
                   "slider": range(1, 21)})


def content(request):
    article_id = request.GET.get("article")
    try:
        a = Article.objects.get(id=article_id)
        sections = [{"title": s.title, "content": s.content}
                    for s in a.section_set.all()]
        d = {"title": a.title, "content": "", "summary": a.summary,
             "sections": sections}
        return JsonResponse(d)
    except Article.DoesNotExist:
        raise Http404("No such article: {0}.".format(article_id))


def _cosine_similarity(v1, v2):
    sumxx, sumxy, sumyy = 0, 0, 0
    for i in range(len(v1)):
        x = v1[i]
        y = v2[i]
        sumxx += x * x
        sumyy += y * y
        sumxy += x * y
    return sumxy / math.sqrt(sumxx * sumyy)


def _dot_product(v1, v2):
    return sum(map(operator.mul, v1, v2))


def article_match_with_silders(current, sliders):
    a = sliders
    qs = ArticleAttr.objects.select_related("article").\
        exclude(article__id=current)
    for attr in qs:
        sim = _get_sim(current, attr.article.id)
        # b = (attr.length, attr.media, sim, attr.care)
        b = (attr.media, sim, attr.care, attr.reading)
        score = _cosine_similarity(a, b)
        # score = _dot_product(a, b)
        yield (attr, score, sim)


def _get_sim(a, b):
    if a == b:
        return 20

    # Retrieve similarity values if needed.
    global ALL_SIM
    if ALL_SIM is None:
        qs = ArticleSimilarity.objects.all()
        ALL_SIM = dict(((row.a, row.b), row.similarity) for row in qs)

    key = (a, b) if a < b else (b, a)
    return ALL_SIM.get(key, 0)


def catch_fish(request):
    article_id = int(request.GET.get("article"))
    sliders = list(map(int, request.GET.getlist("sliders[]")))
    assert len(sliders)

    angles = (a for a in range(0, sys.maxsize, 60))
    all_results = sorted(article_match_with_silders(article_id, sliders),
                         key=lambda x: x[1],
                         reverse=True)
    all_results = sorted(all_results[0:10], key=lambda x: x[0].article.title)

    result = list()
    rank = 0
    for r in all_results:
        attr, score, sim = r
        # Compute length with similarity
        # l = max((SLIDER_MAX - sim) / SLIDER_MAX * CENTER.y * 1,
        #         CENTER_DISTANCE_MIN)

        # Compute length with slider matching.
        l = score * CENTER.y * 0.75
        angle = next(angles)
        dx = int(l * math.cos(angle))    # Compute x and y offsets.
        dy = int(l * math.sin(angle))
        dx += randint(0, 5)
        dy += randint(0, 5)
        fish_str_id = "fish{0}".format(attr.article.id)
        result.append({"id": attr.article.id,
                       "sid": fish_str_id,
                       "rank": rank,
                       "title": attr.article.title,
                       "score": score,
                       "similarity": sim})
        rank += 1

    # Do overlap removal.
    # or_list = [FishRect(f["dx"], f["dy"], 120, 50, k) for k, f in result.items()]
    # remove_overlap(or_list)
    # for r in or_list:
    #     result[r.fish_id]["dx"] = r.x
    #     result[r.fish_id]["dy"] = r.y

    return JsonResponse({"result": result})


def overlap_removal_test(request):
    class TestRect(Rectangle):
        name = None

    rects = list()
    # rects.append(TestRect(250, 250, 6, 6))
    # rects.append(TestRect(248, 249, 5, 5))
    # rects.append(TestRect(291, 208, 5, 5))
    # rects.a‰ppend(TestRect(163, 278, 5, 5))
    # rects.append(TestRect(259, 268, 5, 5))
    # rects.append(TestRect(323, 215, 67, 67))
    # rects.append(TestRect(226, 238, 5, 5))
    # rects.append(TestRect(331, 321, 5, 5))
    # rects.append(TestRect(263, 253, 5, 5))
    # rects.append(TestRect(298, 193, 5, 5))
    # rects.append(TestRect(244, 238, 5, 5))
    # rects.append(TestRect(233, 272, 5, 5))
    # rects.append(TestRect(259, 227, 5, 5))
    # rects.append(TestRect(219, 250, 5, 5))
    # rects.append(TestRect(294, 319, 5, 5))
    # rects.append(TestRect(249, 225, 5, 5))
    # rects.append(TestRect(170, 180, 5, 5))
    # rects.append(TestRect(271, 244, 5, 5))
    # rects.append(TestRect(163, 330, 5, 5))
    # rects.append(TestRect(250, 280, 5, 5))
    # rects.append(TestRect(237, 247, 5, 5))
    # rects.append(TestRect(240, 263, 5, 5))
    # rects.append(TestRect(229, 255, 5, 5))
    # rects.append(TestRect(255, 238, 5, 5))
    # rects.append(TestRect(234, 224, 5, 5))
    # rects.append(TestRect(331, 236, 5, 5))
    # rects.append(TestRect(249, 268, 5, 5))
    # rects.append(TestRect(211, 195, 76, 76))
    # rects.append(TestRect(270, 265, 5, 5))
    for i in range(0, 50):
        x = randint(0, 200) + 200
        y = randint(0, 100) + 100
        w = randint(0, 50) + 50
        h = randint(0, 50) + 50
        r = TestRect(x, y, w, h)
        r.name = str(i)
        rects.append(r)
    import copy
    new_rects = copy.deepcopy(rects)
    remove_overlap(new_rects)
    return render(request, "ortest.html", {"rects": rects, "nr": new_rects})
