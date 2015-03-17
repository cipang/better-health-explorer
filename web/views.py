from django.shortcuts import render
from django.http import Http404, JsonResponse
from extract.models import Article
from web.models import ArticleAttr
from random import randint
from collections import namedtuple
import math, operator, sys


Point = namedtuple("Point", ["x", "y"])
CENTER = Point(130, 160)
SLIDER_MAX = 20
CENTER_DISTANCE_MIN = 100


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


def article_match_with_silders(sliders):
    a = sliders
    for attr in ArticleAttr.objects.select_related("article"):
        b = (attr.length, attr.media)
        dot_product = sum(map(operator.mul, a, b))
        yield (attr, dot_product)


def catch_fish(request):
    article_id = request.GET.get("article")
    sliders = list(map(int, request.GET.getlist("sliders[]")))
    assert len(sliders)

    angles = (a for a in range(0, sys.maxsize, 60))
    all_results = sorted(article_match_with_silders(sliders),
                         key=lambda x: x[1],
                         reverse=True)

    result = dict()
    for r in all_results[0:10]:
        attr, score = r
        sim = attr.similarity
        # Compute length with similarity
        l = max((SLIDER_MAX - sim) / SLIDER_MAX * CENTER.y,
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
