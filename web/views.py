from django.shortcuts import render
from django.http import Http404, JsonResponse
from extract.models import Article
from web.models import *
from random import randint
from collections import namedtuple
import math, operator, sys


Point = namedtuple("Point", ["x", "y"])
CENTER = Point(130, 160)
SLIDER_MAX = 20
CENTER_DISTANCE_MIN = 100

ALL_SIM = None


def home(request):
    return render(request, "home.html",
                  {"loop": range(0, 20),
                   "slider": range(1, 21)})


def content(request):
    article_id = request.GET.get("article")
    try:
        a = Article.objects.get(id=article_id)
        d = {"title": a.title, "content": a.content}
        return JsonResponse(d)
    except Article.DoesNotExist:
        raise Http404("No such article: {0}.".format(article_id))


def article_match_with_silders(current, sliders):
    a = sliders
    qs = ArticleAttr.objects.select_related("article").\
        exclude(article__id=current)
    for attr in qs:
        sim = _get_sim(current, attr.article.id)
        b = (attr.length, attr.media, sim)
        dot_product = sum(map(operator.mul, a, b))
        yield (attr, dot_product, sim)


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

    result = dict()
    for r in all_results[0:10]:
        attr, score, sim = r
        # Compute length with similarity
        l = max((SLIDER_MAX - sim) / SLIDER_MAX * CENTER.y * 1.5,
                CENTER_DISTANCE_MIN)
        angle = next(angles)
        dx = int(l * math.cos(angle))    # Compute x and y offsets.
        dy = int(l * math.sin(angle))
        # dx += int(sliders[0]) * 5
        # dy += int(sliders[1]) * 5
        fish_str_id = "fish{0}".format(attr.article.id)
        result[fish_str_id] = ({"id": attr.article.id,
                                "title": attr.article.title,
                                "score": score,
                                "similarity": sim,
                                "dx": dx,
                                "dy": dy})
    return JsonResponse({"result": result})
