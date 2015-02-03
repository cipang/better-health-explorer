from django.contrib import admin
from .models import Article, Image, OutLink


class ImageInline(admin.TabularInline):
    model = Image
    extra = 1


class OutLinkInline(admin.TabularInline):
    model = OutLink
    extra = 1


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ["pk", "title", "last_modified"]
    list_display_links = ["title"]
    inlines = [ImageInline, OutLinkInline]
    search_fields = ["title"]


@admin.register(Image, OutLink)
class DefaultAdmin(admin.ModelAdmin):
    pass
