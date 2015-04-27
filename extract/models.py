from django.db import models


class Article(models.Model):
    source = models.CharField(max_length=5)
    url = models.URLField(null=True, default=None, blank=True)
    title = models.CharField(max_length=200)
    summary = models.TextField()
    content = models.TextField()
    category = models.CharField(max_length=200, blank=True)
    remarks = models.CharField(max_length=150, null=True, blank=True)
    last_modified = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Article"
        verbose_name_plural = "Articles"

    def __str__(self):
        return self.title


class Image(models.Model):
    article = models.ForeignKey(Article)
    src = models.URLField()
    alt = models.CharField(max_length=200)

    class Meta:
        verbose_name = "Image"
        verbose_name_plural = "Images"

    def __str__(self):
        return str(self.pk)


class OutLink(models.Model):
    article = models.ForeignKey(Article)
    target_source = models.CharField(max_length=5)
    target_url = models.URLField()
    alt = models.CharField(max_length=200)

    class Meta:
        verbose_name = "OutLink"
        verbose_name_plural = "OutLinks"

    def __str__(self):
        return str(self.pk)
