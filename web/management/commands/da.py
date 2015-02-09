from django.core.management.base import BaseCommand, CommandError
from extract.models import *
from web.models import *
from bs4 import BeautifulSoup
import math


class Stats:
    max_image_count = 0
    max_word_count = 0

    def __init__(self):
        self.image_count = 0
        self.word_count = 0

    def __setattr__(self, name, value):
        if name == "image_count" and value > Stats.max_image_count:
            Stats.max_image_count = value
        elif name == "word_count" and value > Stats.max_word_count:
            Stats.max_word_count = value
        object.__setattr__(self, name, value)

    def __str__(self):
        return "Images: {0} (Max: {1}); Words: {2} (Max: {3}).".format(
            self.image_count, Stats.max_image_count,
            self.word_count, Stats.max_word_count)


class Command(BaseCommand):
    args = ""
    help = "Run data analysis"

    @staticmethod
    def normalize(x, max_x, max_output=20, cast=math.ceil):
        return cast((float(x) / float(max_x)) * max_output)

    def handle(self, *args, **options):
        result = self.compute_stats()
        for article, stats in result.items():
            aa = ArticleAttr(article=article)
            aa.length = self.normalize(stats.word_count, Stats.max_word_count)
            aa.media = self.normalize(stats.image_count, Stats.max_image_count)
            aa.is_local = article.source in ("BHC")
            print(aa)

    def compute_stats(self):
        d = dict()
        qs = Article.objects.all().prefetch_related("image_set")
        for article in qs:
            stats = Stats()
            d[article] = stats
            stats.image_count = article.image_set.count()
            soup = BeautifulSoup(article.content)
            stats.word_count = len(soup.get_text().split(" "))
        return d
