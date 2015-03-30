from django.core.management.base import BaseCommand, CommandError, make_option
from extract.models import *
from web.models import *
from bs4 import BeautifulSoup
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
from random import randint
from . import readability
import math
import os
import re


class Stats:
    max_image_count = 0
    max_word_count = 0
    max_co_word_count = 0
    max_reading = 0

    def __init__(self):
        self.image_count = 0
        self.word_count = 0
        self.co_word = 0
        self.reading = 0

    def __setattr__(self, name, value):
        if name == "image_count" and value > Stats.max_image_count:
            Stats.max_image_count = value
        elif name == "word_count" and value > Stats.max_word_count:
            Stats.max_word_count = value
        elif name == "co_word_count" and value > Stats.max_co_word_count:
            Stats.max_co_word_count = value
        elif name == "reading" and value > Stats.max_reading:
            Stats.max_reading = value
        object.__setattr__(self, name, value)


class Command(BaseCommand):
    args = ""
    help = "Run data analysis"
    option_list = BaseCommand.option_list + (
        make_option("--sim", action="store_true", dest="sim",
                    default=False, help="Run similarity computation."),
    )

    @staticmethod
    def normalize(x, max_x, max_output=20, cast=math.ceil):
        if max_x == 0:
            return 0
        result = cast((float(x) / float(max_x)) * max_output)
        return max(min(max_output, result), 0)

    def extract_words(self, text):
        content = text.lower()
        tokens = self.tokenizer.tokenize(content)
        return set(w for w in tokens if w not in self.stopwords)

    def get_article_text(self, article):
        soup = BeautifulSoup(article.content)
        return soup.get_text()

    def handle(self, *args, **options):
        self.stdout.write("Current NLTK data path: " + os.environ["NLTK_DATA"])

        self.stdout.write("Computing stats...")
        result = self.compute_stats()
        for article, stats in result.items():
            try:
                aa = ArticleAttr.objects.get(article=article)
            except ArticleAttr.DoesNotExist:
                aa = ArticleAttr(article=article)
            aa.length = self.normalize(stats.word_count, Stats.max_word_count)
            aa.media = self.normalize(stats.image_count, Stats.max_image_count)
            aa.care = stats.care
            aa.reading = self.normalize(stats.reading, Stats.max_reading)
            aa.is_local = article.source in ("BHC")
            aa.save()

        if options["sim"]:
            self.stdout.write("Computing similarity values...")
            result = self.compute_similarity()
            for a, b, stats in result:
                try:
                    row = ArticleSimilarity.objects.get(a=a, b=b)
                except ArticleSimilarity.DoesNotExist:
                    row = ArticleSimilarity(a=a, b=b)
                row.similarity = self.normalize(stats.co_word_count,
                                                Stats.max_co_word_count)
                if stats.linked_flag:
                    row.similarity = self.normalize(row.similarity + 10, 20)
                row.save()

    def compute_stats(self):
        re_care = re.compile(r"\b(care|caring|manage|managing|management|family)\b",
                             flags=re.IGNORECASE)
        re_cond = re.compile(r"\b(condition[s]?|treatment[s]?)\b",
                             flags=re.IGNORECASE)

        d = dict()
        qs = Article.objects.all().prefetch_related("image_set")
        for article in qs:
            stats = Stats()
            d[article] = stats

            # Compute number of images.
            stats.image_count = article.image_set.count()

            # Compute length.
            content = self.get_article_text(article)
            stats.word_count = len(content.split(" "))

            # Compute reading level.
            stats.reading = readability.grade_level(content)

            # Compute article nature: caring <-> conditions
            t, c = article.title, article.category
            if re_care.search(t) or re_care.search(c):
                stats.care = randint(1, 7)
            elif re_cond.search(t) or re_cond.search(c):
                stats.care = randint(13, 20)
            else:
                stats.care = randint(8, 12)

        return d

    def compute_similarity(self):
        l = list()
        c = 0
        qs1 = Article.objects.order_by("id").prefetch_related("outlink_set")
        for a in qs1:
            qs2 = Article.objects.filter(id__gt=a.id).order_by("id")
            a_links = set(x.alt.lower() for x in a.outlink_set.all())
            a_words = self.extract_words(self.get_article_text(a))
            for b in qs2:
                assert a.id < b.id
                b_words = self.extract_words(self.get_article_text(b))
                stats = Stats()
                stats.co_word_count = len(a_words & b_words)
                stats.linked_flag = b.title.lower() in a_links
                l.append((a.id, b.id, stats))
                c += 1
                if c % 100 == 0:
                    self.stdout.write("{0} records written.".format(c))
        return l

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tokenizer = RegexpTokenizer(r'[a-z]+')
        self.stopwords = set(stopwords.words("english"))
