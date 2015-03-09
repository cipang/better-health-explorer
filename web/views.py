from django.shortcuts import render
from django.http import Http404, JsonResponse
from extract.models import Article


def home(request):
    return render(request, "home.html", {"loop": range(0, 20)})


def content(request):
    article_id = request.GET.get("article")
    try:
        a = Article.objects.get(id=article_id)
        d = {"title": a.title, "content": a.content}
        return JsonResponse(d)
    except Article.DoesNotExist:
        raise Http404("No such article: {0}.".format(article_id))
