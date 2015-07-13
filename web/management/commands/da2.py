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
        "Services and support": "#ffa500",
        "": "#da70d6",
        "Video": "#da70d6"
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
            self.compute_similarity()

    @staticmethod
    def get_article_text(article):
        """Return the text content of an article without HTML tags."""
        soup = BeautifulSoup(article.content)
        return soup.get_text()

    def compute_metadata(self):
        re_care = re.compile(r"\b(care|caring|manage|managing|management|family)\b",
                             flags=re.IGNORECASE)
        re_cond = re.compile(r"\b(condition[s]?|treatment[s]?)\b",
                             flags=re.IGNORECASE)

        l = list()
        qs = Article.objects.all()
        bar = self.new_bar()
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

    @staticmethod
    def sort_and_rank(metadata_list, key, reverse, attr):
        self.stdout.write("\t" + attr)
        metadata_list.sort(key=key, reverse=reverse)
        for rank, i, metadata in even_distribute(metadata_list, SLIDER_MIN, SLIDER_MAX):
            setattr(metadata, attr, rank)

    @staticmethod
    def new_bar():
        return Bar(width=20,
                   suffix="%(percent)d%% %(index)d/%(max)d %(elapsed_td)s ETA %(eta_td)s")

    def compute_similarity(self):
        if ArticleSimilarity.objects.first():
            raise CommandError("Clear the ArticleSimilarity table first.")

        self.stdout.write("Caching all article IDs...")
        all_article_ids = list(Article.objects.values_list("id", flat=True).order_by("id"))
        # all_article_ids = all_article_ids[100:160]

        def get_info(a):
            words = text_to_vector(self.get_article_text(a))
            links = set(x.target_url for x in a.outlink_set.all())
            cats = set(x.name for x in a.category3_set.all()) or set(x.name for x in a.category35_set.all())
            keywords = set(x.name for x in a.keyword_set.all())
            provider = a.provider
            return (words, links, cats, keywords, provider)

        def percent(x, y):
            return x / y if y else 0.0

        bar = self.new_bar()
        self.stdout.write("Computing similarity...")
        cossim_db = defaultdict(dict)
        for i, a_id in enumerate(bar.iter(all_article_ids)):
            a = Article.objects.get(id=a_id)
            a_info = get_info(a)
            for j, b_id in enumerate(all_article_ids[i + 1:]):
                b = Article.objects.get(id=b_id)
                assert a_id < b_id
                b_info = get_info(b)

                # Compare each component.
                sim_words = cosine_similarity(a_info[0], b_info[0])
                sim_links = 1.0 if b.unique_key in a_info[1] or a.unique_key in b_info[1] else 0.0
                sim_cats = percent(len(a_info[2] & b_info[2]), len(a_info[2]))
                sim_keywords = percent(len(a_info[3] & b_info[3]), len(a_info[3]))
                sim_provider = 1.0 if a_info[4] == b_info[4] else 0.0

                cossim = sim_words * 0.2 + sim_links * 0.3 + sim_cats * 0.2 + \
                    sim_keywords * 0.2 + sim_provider * 0.1
                cossim_db[a.id][b.id] = cossim
                # print(sim_words, sim_links, sim_cats, sim_keywords, sim_provider, cossim)
            # End inner for loop.

        bar = self.new_bar()
        self.stdout.write("Sorting similarity...")
        for i in bar.iter(all_article_ids):
            cossim_list = list()
            for j in all_article_ids:
                if i == j:
                    continue
                ki, kj = (i, j) if i < j else (j, i)
                cossim_list.append((i, j, cossim_db[ki][kj]))

            # Sort the cossim.
            cossim_list.sort(key=lambda x: x[2])
            for g, i, t in even_distribute(cossim_list, SLIDER_MIN, SLIDER_MAX):
                ArticleSimilarity.objects.create(a=t[0], b=t[1], similarity=g)

    def choose_color(self, article):
        if article.source != "BHC":
            return self._colors["Video"]
        else:
            return self._colors.get(article.cat2, "")
