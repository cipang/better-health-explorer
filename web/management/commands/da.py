from django.core.management.base import BaseCommand, CommandError
from extract.models import *
from web.models import *
from bs4 import BeautifulSoup
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
import math


class Stats:
    max_image_count = 0
    max_word_count = 0
    max_co_word_count = 0

    def __init__(self):
        self.image_count = 0
        self.word_count = 0
        self.co_word = 0

    def __setattr__(self, name, value):
        if name == "image_count" and value > Stats.max_image_count:
            Stats.max_image_count = value
        elif name == "word_count" and value > Stats.max_word_count:
            Stats.max_word_count = value
        elif name == "co_word_count" and value > Stats.max_co_word_count:
            Stats.max_co_word_count = value
        object.__setattr__(self, name, value)


class Command(BaseCommand):
    args = ""
    help = "Run data analysis"

    @staticmethod
    def normalize(x, max_x, max_output=20, cast=math.ceil):
        return cast((float(x) / float(max_x)) * max_output)

    def extract_words(self, text):
        content = text.lower()
        tokens = self.tokenizer.tokenize(content)
        return set(w for w in tokens if w not in self.stopwords)

    def get_article_text(self, article):
        soup = BeautifulSoup(article.content)
        return soup.get_text()

    def handle(self, *args, **options):
        result = self.compute_stats()
        for article, stats in result.items():
            try:
                aa = ArticleAttr.objects.get(article=article)
            except ArticleAttr.DoesNotFound:
                aa = ArticleAttr(article=article)
            aa.length = self.normalize(stats.word_count, Stats.max_word_count)
            aa.media = self.normalize(stats.image_count, Stats.max_image_count)
            aa.similarity = self.normalize(stats.co_word_count,
                                           Stats.max_co_word_count)
            if stats.linked_flag:
                aa.similarity += 10
            aa.is_local = article.source in ("BHC")
            aa.save()

    def compute_stats(self):
        # For similarity, temporary use Diabetes as the base page.
        diabetes = Article.objects.get(title="Diabetes")
        diabetes_words = self.extract_words(self.get_article_text(diabetes))
        diabetes_links = set(l.alt.lower() for l in diabetes.outlink_set.all())

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

            # Compute similarity.
            article_words = self.extract_words(content)
            stats.co_word_count = len(article_words & diabetes_words)
            stats.linked_flag = False
            if article.title.lower() in diabetes_links:
                self.stdout.write("{0} linked to Diabetes.".format(
                    article.title))
                stats.linked_flag = True
        return d

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tokenizer = RegexpTokenizer(r'[a-z]+')
        self.stopwords = set(stopwords.words("english"))
