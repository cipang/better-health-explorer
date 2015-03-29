from django.db import models
from extract.models import Article


class ArticleAttr(models.Model):
    article = models.OneToOneField(Article)
    length = models.SmallIntegerField(default=0)
    media = models.SmallIntegerField(default=0)
    care = models.SmallIntegerField(default=0)
    reading = models.SmallIntegerField(default=0)
    is_video = models.BooleanField(default=False)
    is_local = models.BooleanField(default=False)

    class Meta:
        verbose_name = "ArticleAttr"
        verbose_name_plural = "ArticleAttrs"

    def __str__(self):
        return "{0} {1} {2}".format(
            self.article if self.article_id else None,
            self.length,
            self.media)


class ArticleSimilarity(models.Model):
    a = models.IntegerField("Article A (with smaller ID)")
    b = models.IntegerField("Article B (with bigger ID)")
    similarity = models.SmallIntegerField(default=0)

    class Meta:
        verbose_name = "ArticleSimilarity"
        verbose_name_plural = "ArticleSimilarity"
        unique_together = [("a", "b")]

    def __str__(self):
        return "{0} {1} {2}".format(self.a, self.b, self.similarity)


class Section(models.Model):
    article = models.ForeignKey(Article)
    section_no = models.IntegerField("Section No.")
    title = models.CharField("Section Title", max_length=150)
    content = models.TextField("Section Content")

    class Meta:
        verbose_name = "Section"
        verbose_name_plural = "Sections"

    def __str__(self):
        return "{0} {1}".format(self.article_id, self.section_no)
