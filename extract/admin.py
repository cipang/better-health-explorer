from django.contrib import admin
from .models import Article, Image


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("pk", "title", "last_modified")
    list_display_links = ("title",)
    search_fields = ("title",)


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ("pk", "article", "alt")
