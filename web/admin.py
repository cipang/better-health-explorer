from django.contrib import admin
from .models import *


@admin.register(ArticleAttr)
class ArticleAttrAdmin(admin.ModelAdmin):
    list_display = ["article", "length", "media", "care", "reading"]


@admin.register(ArticleSimilarity)
class SimilarityAdmin(admin.ModelAdmin):
    list_display = ["a", "b", "similarity"]


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ["article", "section_no", "title"]
