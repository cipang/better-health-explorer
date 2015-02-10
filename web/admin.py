from django.contrib import admin
from .models import ArticleAttr


@admin.register(ArticleAttr)
class DefaultAdmin(admin.ModelAdmin):
    pass
