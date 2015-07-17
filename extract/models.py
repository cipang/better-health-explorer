from django.db import models


class Article(models.Model):
    source = models.CharField(max_length=5)
    url = models.URLField(null=True, default=None, blank=True)
    unique_key = models.CharField(max_length=200, unique=True, null=True, blank=True, default=None)
    title = models.CharField(max_length=200)
    summary = models.TextField()
    content = models.TextField()
    category = models.CharField(max_length=200, blank=True)
    cat2 = models.CharField(max_length=200, blank=True)
    provider = models.CharField(max_length=200, blank=True)
    remarks = models.CharField(max_length=150, null=True, blank=True)
    last_modified = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Article"
        verbose_name_plural = "Articles"

    def __str__(self):
        return "{0}: {1}".format(self.id, self.title)


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


class Category3(models.Model):
    article = models.ForeignKey(Article)
    name = models.CharField("Category 3 Name", max_length=200)

    class Meta:
        verbose_name = "Category3"
        verbose_name_plural = "Category3"

    def __str__(self):
        return self.name


class Category35(models.Model):
    article = models.ForeignKey(Article)
    name = models.CharField("Category 35 Name", max_length=200)

    class Meta:
        verbose_name = "Category35"
        verbose_name_plural = "Category35"

    def __str__(self):
        return self.name


class Keyword(models.Model):
    article = models.ForeignKey(Article)
    name = models.CharField("Keyword", max_length=200, db_index=True)

    class Meta:
        verbose_name = "Keyword"
        verbose_name_plural = "Keywords"

    def __str__(self):
        return self.name
