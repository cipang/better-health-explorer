from django.db import models
from extract.models import Article
from collections import Counter
import math


class ArticleAttr(models.Model):
    article = models.OneToOneField(Article, on_delete=models.DO_NOTHING)
    length = models.SmallIntegerField(default=0)
    media = models.SmallIntegerField(default=0)
    care = models.SmallIntegerField(default=0)
    reading = models.SmallIntegerField(default=0)
    is_video = models.BooleanField(default=False)
    is_local = models.BooleanField(default=False)
    color = models.CharField(max_length=20, blank=True)

    class Meta:
        verbose_name = "ArticleAttr"
        verbose_name_plural = "ArticleAttrs"

    def __str__(self):
        return "{0} {1} {2} {3}".format(
            self.article if self.article_id else None,
            self.media,
            self.care,
            self.reading)


class ArticleSimilarity(models.Model):
    a = models.IntegerField("Article A (with smaller ID)")
    b = models.IntegerField("Article B (with bigger ID)")
    similarity = models.SmallIntegerField(default=0)
    raw_value = models.FloatField(default=0.0)

    class Meta:
        verbose_name = "ArticleSimilarity"
        verbose_name_plural = "ArticleSimilarity"
        unique_together = [("a", "b")]

    def __str__(self):
        return "{0} {1} {2}".format(self.a, self.b, self.similarity)


class Section(models.Model):
    article = models.ForeignKey(Article, on_delete=models.DO_NOTHING)
    section_no = models.IntegerField("Section No.")
    title = models.CharField("Section Title", max_length=150)
    content = models.TextField("Section Content")

    class Meta:
        verbose_name = "Section"
        verbose_name_plural = "Sections"
        ordering = ["article", "section_no"]

    def __str__(self):
        return "{0} {1}".format(self.article_id, self.section_no)


class MainTopic(models.Model):
    name = models.CharField("Topic name", max_length=80)
    article_id = models.IntegerField("Linked to article ID")

    class Meta:
        verbose_name = "Main Topic"
        verbose_name_plural = "Main Topics"
        ordering = ["name"]

    def __str__(self):
        return "{0} ({1})".format(self.name, self.article_id)


# Usage: distribution(x.care for x in ArticleAttr.objects.all())
def distribution(things, printed=False):
    c = Counter(things)
    dist = [(e, c[e]) for e in sorted(c)]
    if printed:
        for item in dist:
            print("{0}\t{1}".format(*item))
    return dist


def even_distribute(collection, group_min, group_max):
    max_per_group = math.ceil(len(collection) / (group_max - group_min + 1))
    group, index = group_min, 0
    for x in collection:
        yield (group, index, x)
        index += 1
        if index >= max_per_group:
            group += 1
            index = 0
