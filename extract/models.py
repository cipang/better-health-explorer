from django.db import models


class Article(models.Model):
    source = models.CharField(max_length=5)
    url = models.URLField(null=True, default=None)
    title = models.CharField(max_length=200)
    summary = models.TextField()
    content = models.TextField()
    category = models.CharField(max_length=200)
    remarks = models.CharField(max_length=150, null=True)
    last_modified = models.DateTimeField(null=True)

    class Meta:
        verbose_name = "Article"
        verbose_name_plural = "Articles"

    def __str__(self):
        return self.title


class Image(models.Model):
    article = models.ForeignKey(Article)
    src = models.URLField()
    alt = models.CharField(max_length=50)

    class Meta:
        verbose_name = "Image"
        verbose_name_plural = "Images"

    def __str__(self):
        return str(self.pk)
