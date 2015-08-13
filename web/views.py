from django.shortcuts import render, get_object_or_404
from django.http import Http404, JsonResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.conf import settings
from django.db.models import Q
from django.core.urlresolvers import reverse
from extract.models import Article
from web.models import *
from web.overlapremoval import Rectangle, remove_overlap
from random import randint
from functools import lru_cache, reduce
# from collections import namedtuple
import math
import operator
import re


# Point = namedtuple("Point", ["x", "y"])
# CENTER = Point(130, 160)
SLIDER_MIN = 1
SLIDER_MAX = 20
# CENTER_DISTANCE_MIN = 100
# ALL_SIM = None
CAT2_LIST = ("Conditions and treatments", "Healthy living",
             "Relationships and family", "Services and support", "Video")


# class FishRect(Rectangle):

#     """Displayed rectangle of each fish. For overlap removal."""

#     def __init__(self, x, y, width, height, fish_id):
#         super(FishRect, self).__init__(x, y, width, height)
#         self.fish_id = fish_id


def home(request):
    if _check_login(request):
        return render(request, "home.html", {"topics": MainTopic.objects.all()})
    else:
        return HttpResponseRedirect(reverse("login"))


def article(request, pk):
    if _check_login(request):
        return render(request, "article.html", {"loop": range(0, 20),
                                                "slider": range(1, 21),
                                                "pk": pk})
    else:
        return HttpResponseRedirect(reverse("login"))


def content(request):
    article_id = request.GET.get("article")
    try:
        a = Article.objects.get(id=article_id)
        sections = [{"title": s.title, "content": s.content}
                    for s in a.section_set.all()]
        content = a.content if not sections else ""
        d = {"title": a.title, "content": content, "summary": a.summary,
             "sections": sections}
        return JsonResponse(d)
    except Article.DoesNotExist:
        raise Http404("No such article: {0}.".format(article_id))


def summary(request):
    article_id = request.GET.get("article")
    try:
        a = Article.objects.get(id=article_id)
        d = {"title": a.title, "summary": a.summary}
        return JsonResponse(d)
    except Article.DoesNotExist:
        raise Http404("No such article: {0}.".format(article_id))


def _cosine_similarity(v1, v2):
    sumxx, sumxy, sumyy = 0, 0, 0
    for i in range(len(v1)):
        x, y = v1[i], v2[i]
        sumxx += x * x
        sumyy += y * y
        sumxy += x * y
    return sumxy / math.sqrt(sumxx * sumyy)


def _dot_product(v1, v2):
    return sum(map(operator.mul, v1, v2))


def article_match_with_silders(current, sliders, checkboxes, filters):
    # a = sliders
    # qs = ArticleAttr.objects.select_related("article").\
    #     exclude(article__id=current)
    # for attr in qs:
    #     sim = _get_sim(current, attr.article.id)
    #     # b = (attr.length, attr.media, sim, attr.care)
    #     b = (attr.media, sim, attr.care, attr.reading)
    #     score = _cosine_similarity(a, b)
    #     # score = _dot_product(a, b)
    #     yield (attr, score, sim)

    # First use similarity to filter, then compute score within the result pool.
    sim = sliders[0]
    # a = sliders + [randint(1, 10)]

    # Obtains the selected dimensions.
    a = [x[1] for x in zip(checkboxes, sliders) if x[0]]

    # Obtains other articles and compares their similarities.
    other_articles = _get_articles_for(current, filters)
    sim_dict = _get_all_sims(current)
    pool = [(x, sim_dict.get(x, 0.0)) for x in other_articles]
    pool.sort(key=lambda x: abs(x[1] - sim))
    pool = map(lambda x: x[0], pool[0:100])
    result = list()
    for attr in ArticleAttr.objects.select_related("article").filter(article__id__in=pool):
        # b = (attr.media, attr.care, attr.reading, randint(1, 10))
        attr_sim = sim_dict[attr.article_id]
        v = (attr_sim, attr.media, attr.care, attr.reading)
        b = [x[1] for x in zip(checkboxes, v) if x[0]]
        score = _cosine_similarity(a, b)
        result.append((attr, score, attr_sim))
    return result


@lru_cache()
def _get_articles_for(current, filters):
    qs = Article.objects.exclude(id=current)
    # Add filters if necessary.
    if not all(filters):
        query = reduce(operator.or_,
                       (Q(cat2=x[1]) for x in zip(filters, CAT2_LIST) if x[0]))
        qs = qs.filter(query)
    return list(qs.values_list("id", flat=True))


@lru_cache()
def _get_all_sims(a):
    return {x.b: x.similarity for x in ArticleSimilarity.objects.filter(a=a)}


def catch_fish(request):
    article_id = int(request.GET.get("article"))
    sliders = tuple(map(int, request.GET.getlist("sliders[]")))
    checkboxes = tuple(map(lambda x: x == "true",
                           request.GET.getlist("checkboxes[]")))
    filters = tuple(map(lambda x: x == "true",
                        request.GET.getlist("filters[]")))
    assert len(sliders) and len(checkboxes) == len(sliders) and \
        checkboxes[0] and any(filters)

    all_results = article_match_with_silders(article_id,
                                             sliders,
                                             checkboxes,
                                             filters)
    # Sort result by the score.
    all_results.sort(key=lambda x: x[1], reverse=True)

    # all_results = sorted(all_results, key=lambda x: x[0].article.title)
    # all_results = all_results

    tier0, tier1, tier2 = list(), list(), list()
    last_score = None
    order = 0
    for row in all_results:
        attr, score, sim = row

        # Text-based attributes.
        fish_str_id = "fish{0}".format(attr.article.id)
        title = attr.article.title
        if len(title) >= 36:
            title = title[0:36].strip() + "..."

        # Create a fish "object".
        fish = {"id": attr.article.id,
                "sid": fish_str_id,
                "order": order,
                "title": title,
                "score": score,
                "similarity": sim,
                "color": attr.color}

        # Choose a tier for the fish.
        margin = 0.001
        if len(tier0) < 3:
            selected_tier = tier0
            fish["tier"] = 0
        elif last_score - score < margin and len(tier0) < 6 and not tier1:
            selected_tier = tier0
            fish["tier"] = 0
        elif len(tier0) + len(tier1) < 12:
            selected_tier = tier1
            fish["tier"] = 1
        else:
            selected_tier = tier2
            fish["tier"] = 2
        selected_tier.append(fish)

        order += 1
        last_score = score
        limit = 72 if len(tier0) == 3 else 57
        if order >= limit:
            break

    result = tier0 + tier1 + tier2
    return JsonResponse({"result": result,
                         "cache_info": [repr(_get_all_sims.cache_info()),
                                        repr(_get_articles_for.cache_info())]})


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


def image_redirect(request, image):
    new_url = settings.STATIC_URL + "article-images/" + image
    return HttpResponseRedirect(new_url)


def find_article(request):
    url = request.GET.get("url")
    if not url:
        return HttpResponseBadRequest("No URL specified.")
    a = get_object_or_404(Article, unique_key=url)
    return JsonResponse({"article": a.id})


# Search code from http://julienphalip.com/post/2825034077/adding-search-to-a-django-site-in-a-snap
def normalize_query(query_string,
                    findterms=re.compile(r'"([^"]+)"|(\S+)').findall,
                    normspace=re.compile(r'\s{2,}').sub):
    ''' Splits the query string in invidual keywords, getting rid of unecessary spaces
        and grouping quoted words together.
        Example:

        >>> normalize_query('  some random  words "with   quotes  " and   spaces')
        ['some', 'random', 'words', 'with quotes', 'and', 'spaces']

    '''
    return [normspace(' ', (t[0] or t[1]).strip()) for t in findterms(query_string)]


def get_query(query_string, search_fields):
    ''' Returns a query, that is a combination of Q objects. That combination
        aims to search keywords within a model by testing the given search fields.

    '''
    query = None  # Query to search for every search term
    terms = normalize_query(query_string)
    for term in terms:
        or_query = None  # Query to search for a given term in each field
        for field_name in search_fields:
            q = Q(**{"%s__icontains" % field_name: term})
            if or_query is None:
                or_query = q
            else:
                or_query = or_query | q
        if query is None:
            query = or_query
        else:
            query = query & or_query
    return query


def search(request):
    q = request.GET.get("q", "")
    result = None
    if q:
        nq = normalize_query(q)
        qs = Article.objects.filter(get_query(q, ("title", "keyword__name"))).\
            select_related("keyword").distinct()
        result = list()
        for article in qs:
            score = 0
            for x in nq:
                for y in [article.title] + [k.name for k in article.keyword_set.all()]:
                    if x in y:
                        score += 1
            result.append((article, score))
        result.sort(key=lambda x: x[1], reverse=True)
        result = result[0:100]
    return render(request, "search_result.html", {"q": q, "result": result})


def login(request):
    msg = ""
    if request.method == "POST":
        if request.POST.get("password") == "21111122":
            redirect = HttpResponseRedirect(reverse("home"))
            redirect.set_signed_cookie("hifish_login", "OK", max_age=86400)
            return redirect
        else:
            msg = "Incorrect username or password."
    return render(request, "login.html", {"msg": msg})


def _check_login(request):
    return request.get_signed_cookie("hifish_login", default=None) == "OK"
