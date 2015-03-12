from django.shortcuts import render
from django.http import Http404, JsonResponse
from extract.models import Article
from web.models import ArticleAttr
from random import randint
from collections import namedtuple
import math


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


def catch_fish(request):
    article_id = request.GET.get("article")
    sliders = request.GET.getlist("sliders[]")
    assert len(sliders)

    # TODO: For demo only.
    start = 1 if int(article_id) == 93 else randint(0, 100)

    sim_records = ArticleAttr.objects.order_by("-similarity").\
        select_related("article")[start:start + 5]
    result = []
    for r in sim_records:
        sim = r.similarity
        # Compute length with similarity
        l = max((SLIDER_MAX - r.similarity) / SLIDER_MAX * CENTER.y,
                CENTER_DISTANCE_MIN)
        angle = math.radians(randint(0, 360))   # Random an angle.
        dx = l * math.cos(angle)    # Compute x and y offsets.
        dy = l * math.sin(angle)
        result.append({"id": r.article.id,
                       "title": r.article.title,
                       "similarity": sim,
                       "dx": dx,
                       "dy": dy})
    return JsonResponse({"result": result})
