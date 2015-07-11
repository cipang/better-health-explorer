from django.contrib import admin
from .models import *


class ImageInline(admin.TabularInline):
    model = Image
    extra = 1


class OutLinkInline(admin.TabularInline):
    model = OutLink
    extra = 1


class Category3Inline(admin.TabularInline):
    model = Category3
    extra = 1


class Category35Inline(admin.TabularInline):
    model = Category35
    extra = 1


class KeywordInline(admin.TabularInline):
    model = Keyword
    extra = 1


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ["pk", "title", "last_modified"]
    list_display_links = ["title"]
    inlines = [KeywordInline, ImageInline, OutLinkInline,
               Category3Inline, Category35Inline]
    search_fields = ["title"]


@admin.register(Image, OutLink)
class DefaultAdmin(admin.ModelAdmin):
    pass
