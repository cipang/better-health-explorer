from django.core.management.base import BaseCommand, CommandError, make_option
from collections.abc import MutableMapping
from extract.models import *
from web.models import *
from web.views import SLIDER_MAX, SLIDER_MIN
from bs4 import BeautifulSoup
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
from random import randint
from . import readability
import math
import os
import sys
import re


class Metadata(MutableMapping):

    """Store metadata of an article and perserve global min/max values for
    normalization.
    """

    max_values = dict()
    min_values = dict()

    def __init__(self, *args, **kwargs):
        self.store = dict()
        self.update(dict(*args, **kwargs))

    def __getitem__(self, key):
        return self.store[key]

    def __setitem__(self, key, value):
        self.store[key] = value
        Metadata.min_values[key] = min(Metadata.min_values.get(key, sys.maxsize), value)
        Metadata.max_values[key] = max(Metadata.max_values.get(key, 0), value)

    def __delitem__(self, key):
        raise NotImplementedError()

    def __iter__(self):
        return iter(self.store)

    def __len__(self):
        return len(self.store)

    def norm(self, key):
        a = self.store[key] - self.min_values[key]
        b = self.max_values[key] - self.min_values[key]
        return 0 if b == 0 else a / b

    def normint(self, key, scale_min=SLIDER_MIN, scale_max=SLIDER_MAX):
        return int(self.norm(key) * (scale_max - scale_min)) + scale_min


class Command(BaseCommand):
    args = ""
    help = "Run data analysis"
    option_list = BaseCommand.option_list + (
        make_option("--sim", action="store_true", dest="sim",
                    default=False, help="Run similarity computation."),
    )

    def extract_words(self, text):
        """Tokenize a string using NLTK and return a set of lowercased words."""
        content = text.lower()
        tokens = self.tokenizer.tokenize(content)
        return set(w for w in tokens if w not in self.stopwords)

    def get_article_text(self, article):
        """Return the text content of an article without HTML tags."""
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
            aa.length = stats.normint("word_count")
            aa.media = stats.media
            aa.care = stats.care
            aa.reading = stats.normint("reading")
            aa.is_local = article.source in ("BHC")
            aa.is_video = article.source in ("BHCYT")
            aa.save()

        if options["sim"]:
            self.stdout.write("Computing similarity values...")
            result = self.compute_similarity()
            for a, b, stats in result:
                try:
                    row = ArticleSimilarity.objects.get(a=a, b=b)
                except ArticleSimilarity.DoesNotExist:
                    row = ArticleSimilarity(a=a, b=b)
                row.similarity = stats.normint("co_word_count")
                if stats.linked_flag:
                    row.similarity = min(SLIDER_MAX, row.similarity + 10)
                row.save()

    def compute_stats(self):
        re_care = re.compile(r"\b(care|caring|manage|managing|management|family)\b",
                             flags=re.IGNORECASE)
        re_cond = re.compile(r"\b(condition[s]?|treatment[s]?)\b",
                             flags=re.IGNORECASE)

        d = dict()
        qs = Article.objects.all().prefetch_related("image_set")
        for article in qs:
            md = Metadata()
            d[article] = md

            # Compute number of images.
            md["image_count"] = article.image_set.count()

            # Compute length.
            content = self.get_article_text(article)
            md["word_count"] = len(content.split(" "))

            # Compute the media dimension based on above two numbers.
            md.media = 11 - md.normint("word_count", 1, 10)
            if md.get("image_count"):
                md.media += md.normint("image_count", 1, 10)

            # Compute reading level.
            md["reading"] = readability.grade_level(content)

            # Compute article nature: caring <-> conditions
            t, c = article.title, article.category
            if re_care.search(t) or re_care.search(c):
                md.care = randint(1, 7)
            elif re_cond.search(t) or re_cond.search(c):
                md.care = randint(13, 20)
            else:
                md.care = randint(8, 12)

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
                md = Stats()
                md["co_word_count"] = len(a_words & b_words)
                md.linked_flag = b.title.lower() in a_links
                l.append((a.id, b.id, md))
                c += 1
                if c % 100 == 0:
                    self.stdout.write("{0} records written.".format(c))
        return l

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tokenizer = RegexpTokenizer(r'[a-z]+')
        self.stopwords = set(stopwords.words("english"))
