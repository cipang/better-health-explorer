from django.core.management.base import BaseCommand, CommandError, make_option
from collections import defaultdict
from extract.models import *
from web.models import *
from web.views import SLIDER_MAX, SLIDER_MIN
from bs4 import BeautifulSoup
from random import randint
from progress.bar import Bar
from .cossim_text import cosine_similarity, text_to_vector
from . import readability
import math
import os
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
        make_option("-s", action="store_true", dest="sim",
                    default=False, help="Run similarity computation."),
        make_option("-a", action="store_true", dest="attr",
                    default=False, help="Run attributes computation."),
    )

    _colors = {
        "Conditions and treatments": "#add8e6",
        "Healthy living": "#98fb98",
        "Relationships and family": "#ffc0cb",
        "Services and support": "#ffe4b5",
        "": "#da70d6"
    }

    def handle(self, *args, **options):
        self.stdout.write("Current NLTK data path: " + os.environ["NLTK_DATA"])
        if not options["sim"] and not options["attr"]:
            raise CommandError("No operation specified in the command line.")

        if options["attr"]:
            self.stdout.write("Computing metadata...")
            result = self.compute_metadata()

            self.stdout.write("Sorting and ranking...")
            self.sort_and_rank(result, lambda x: x.orig_care, False, "care")
            self.sort_and_rank(result, lambda x: x.orig_reading, False, "reading")
            self.sort_and_rank(result, lambda x: x.get_orig_media(), True, "media")

            self.stdout.write("Saving...")
            for md in result:
                article = md.article
                try:
                    aa = ArticleAttr.objects.get(article=article)
                except ArticleAttr.DoesNotExist:
                    aa = ArticleAttr(article=article)
                aa.length = md.orig_word_count
                aa.media = md.media
                aa.care = md.care
                aa.reading = md.reading
                aa.is_local = article.source in {"BHC", "BHCYT"}
                aa.is_video = article.source in {"BHCYT"}
                aa.color = self.choose_color(article)
                aa.save()

        if options["sim"]:
            result = self.compute_similarity()
            for a, b, similarity in result:
                try:
                    row = ArticleSimilarity.objects.get(a=a, b=b)
                except ArticleSimilarity.DoesNotExist:
                    row = ArticleSimilarity(a=a, b=b)
                row.similarity = similarity
                row.save()

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
        bar = Bar(width=20,
                  suffix="%(percent)d%% %(index)d/%(max)d %(elapsed_td)s ETA %(eta_td)s")
        qs = Article.objects.all()
        bar.max = qs.count()
        for article in qs:
            md = Metadata(article)

            # Compute number of images and videos.
            md.orig_image_count = article.image_set.count()
            md.orig_video_count = 1 if article.source in {"BHCYT"} else 0

            # Compute length.
            content = self.get_article_text(article)
            md.orig_word_count = len(content.split(" "))

            # Compute reading level.
            md.orig_reading = readability.grade_level(content)

            # Compute article nature: caring <-> conditions
            keywords = [article.title] + [x.name for x in article.keyword_set.all()]
            care_scale = 0
            for kw in keywords:
                if re_care.search(kw):
                    care_scale -= 1
                if re_cond.search(kw):
                    care_scale += 1
            md.orig_care = abs(care_scale) * 10000 + randint(0, 9999)
            if care_scale < 0:
                md.orig_care *= -1

            # Add the metadata object to the result list.
            l.append(md)
            bar.next()

        # Finish all computations, return the list.
        bar.finish()
        return l

    def sort_and_rank(self, metadata_list, key, reverse, attr):
        self.stdout.write("\t" + attr)
        rank = SLIDER_MIN
        i = 0
        max_objects_per_rank = math.ceil(len(metadata_list) / ((SLIDER_MAX - SLIDER_MIN) + 1))
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
                if i % 1000 == 0:
                    self.stdout.write("\t{0} records processed.".format(i))
        self.stdout.write("\t{0} records processed.".format(i))

        self.stdout.write("Sorting similarity...")
        all_article_ids = sorted(cossim_db.keys())
        for i in all_article_ids:
            cossim_tuples = list()
            n, rank = 0, SLIDER_MIN
            for j in all_article_ids:
                if i == j:
                    continue
                ki, kj = (i, j) if i < j else (j, i)
                cossim_tuples.append((i, j, cossim_db[ki][kj]))
            cossim_tuples.sort(key=lambda x: x[2])      # Sort the cossim.
            max_objects_per_rank = math.ceil(len(cossim_tuples) / ((SLIDER_MAX - SLIDER_MIN) + 1))
            for t in cossim_tuples:
                yield (t[0], t[1], rank)    # Equals to (i, j, rank)
                n += 1
                if n >= max_objects_per_rank:
                    rank += 1
                    n = 0

    def choose_color(self, article):
        if article.source != "BHC":
            return ""
        else:
            return self._colors.get(article.cat2, "")
