from django.db import models
from extract.models import Article


class ArticleAttr(models.Model):
    article = models.OneToOneField(Article)
    similarity = models.SmallIntegerField(default=0)
    length = models.SmallIntegerField(default=0)
    media = models.SmallIntegerField(default=0)
    is_video = models.BooleanField(default=False)
    is_local = models.BooleanField(default=False)

    class Meta:
        verbose_name = "ArticleAttr"
        verbose_name_plural = "ArticleAttrs"

    def __str__(self):
        return "{0} {1} {2} {3}".format(
            self.article if self.article_id else None,
            self.similarity,
            self.length,
            self.media)
