from django.core.management.base import BaseCommand, CommandError, make_option
from collections import defaultdict
from extract.models import *
from web.models import *
from web.views import SLIDER_MAX, SLIDER_MIN
from bs4 import BeautifulSoup
from random import randint
from .cossim_text import cosine_similarity, text_to_vector
from . import readability
import math
import os
import sys
import re


class Metadata(object):

    """Store metadata of an article.
    """

    def __init__(self, article, *args, **kwargs):
        self.orig_word_count = 0
        self.orig_image_count = 0
        self.orig_video_count = 0
        self.orig_care = 0
        self.orig_reading = 0

        self.article = article
        self.length = 0
        self.media = 0
        self.care = 0
        self.reading = 0

    def get_orig_media(self):
        return self.orig_word_count + self.orig_image_count * -1000 + \
            self.orig_video_count * -5000

    def __str__(self):
        return "{0} M={1} C={2} R={3}".format(self.article,
                                              self.media,
                                              self.care,
                                              self.reading)


class Command(BaseCommand):
    args = ""
    help = "Run data analysis (ver. 2)"
    option_list = BaseCommand.option_list + (
        make_option("--sim", action="store_true", dest="sim",
                    default=False, help="Run similarity computation."),
    )

    def handle(self, *args, **options):
        self.stdout.write("Current NLTK data path: " + os.environ["NLTK_DATA"])

        self.stdout.write("Computing metadata...")
        result = self.compute_metadata()
        article_count = len(result)

        self.stdout.write("Sorting and ranking...")
        self.sort_and_rank(result, lambda x: x.orig_care, False, "care")
        self.sort_and_rank(result, lambda x: x.orig_reading, False, "reading")
        self.sort_and_rank(result, lambda x: x.get_orig_media(), True, "media")

        for x in result:
            print(x)

        from web.models import distribution
        print(distribution(x.care for x in result))
        print(distribution(x.reading for x in result))
        print(distribution(x.media for x in result))

        # for md in result:
        #     article = md.article
        #     try:
        #         aa = ArticleAttr.objects.get(article=article)
        #     except ArticleAttr.DoesNotExist:
        #         aa = ArticleAttr(article=article)
        #     aa.length = stats.normint("word_count")
        #     aa.media = stats.media
        #     aa.care = stats.care
        #     aa.reading = stats.normint("reading")
        #     aa.is_local = article.source in ("BHC")
        #     aa.is_video = article.source in ("BHCYT")
        #     aa.save()

        # if options["sim"]:
        #     self.stdout.write("Computing similarity values...")
        #     result = self.compute_similarity()
        #     for a, b, stats in result:
        #         try:
        #             row = ArticleSimilarity.objects.get(a=a, b=b)
        #         except ArticleSimilarity.DoesNotExist:
        #             row = ArticleSimilarity(a=a, b=b)
        #         row.similarity = stats.normint("co_word_count")
        #         if stats.linked_flag:
        #             row.similarity = min(SLIDER_MAX, row.similarity + 10)
        #         row.save()

    def get_article_text(self, article):
        """Return the text content of an article without HTML tags."""
        soup = BeautifulSoup(article.content)
        return soup.get_text()

    def compute_metadata(self):
        re_care = re.compile(r"\b(care|caring|manage|managing|management|family)\b",
                             flags=re.IGNORECASE)
        re_cond = re.compile(r"\b(condition[s]?|treatment[s]?)\b",
                             flags=re.IGNORECASE)

        l = list()
        qs = Article.objects.all().prefetch_related("image_set")
        for article in qs:
            md = Metadata(article)

            # Compute number of images and videos.
            md.orig_image_count = article.image_set.count()
            md.orig_video_count = 1 if article.source in ("BHCYT") else 0

            # Compute length.
            content = self.get_article_text(article)
            md.orig_word_count = len(content.split(" "))

            # Compute reading level.
            md.orig_reading = readability.grade_level(content)

            # Compute article nature: caring <-> conditions
            t, c = article.title, article.category
            if re_care.search(t) or re_care.search(c):
                md.orig_care = randint(1, 1000)
            elif re_cond.search(t) or re_cond.search(c):
                md.orig_care = randint(1001, 2000)
            else:
                md.orig_care = randint(2001, 3000)

            l.append(md)
        return l

    def sort_and_rank(self, metadata_list, key, reverse, attr):
        self.stdout.write("\t" + attr)
        rank = SLIDER_MIN
        i = 0
        max_objects_per_rank = round(len(metadata_list) / ((SLIDER_MAX - SLIDER_MIN) + 1))
        metadata_list.sort(key=key, reverse=reverse)
        for metadata in metadata_list:
            setattr(metadata, attr, rank)
            i += 1
            if i >= max_objects_per_rank:
                rank += 1
                i = 0

    def compute_similarity(self):
        self.stdout.write("Computing similarity...")
        cossim_db = defaultdict(dict)
        i = 0
        qs1 = Article.objects.order_by("id").prefetch_related("outlink_set")
        for a in qs1:
            qs2 = Article.objects.filter(id__gt=a.id).order_by("id")
            a_links = set(x.alt.lower() for x in a.outlink_set.all())
            a_words = text_to_vector(self.get_article_text(a))
            for b in qs2:
                assert a.id < b.id
                b_words = text_to_vector(self.get_article_text(b))
                cossim = cosine_similarity(a_words, b_words)
                # Bonus points if two articles are linked.
                if b.source == "BHC" and b.title.lower() in a_links:
                    cossim += 0.5
                cossim_db[a.id][b.id] = cossim
                i += 1
                if i % 500 == 0:
                    self.stdout.write("\t{0} records processed.".format(c))

        self.stdout.write("Sorting similarity...")
        all_article_ids = sorted(cossim_db.keys())

        return l
