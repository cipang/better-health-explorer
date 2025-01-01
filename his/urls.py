from django.urls import re_path, path
from django.contrib import admin
from web import views

urlpatterns = [
    # Examples:
    # re_path(r'^$', 'his.views.home', name='home'),
    # re_path(r'^blog/', include('blog.urls')),

    re_path(r'^admin/', admin.site.urls),
    re_path(r'^$', views.home, name='home'),
    re_path(r'^login/$', views.login, name='login'),
    re_path(r'^article/(?P<pk>[0-9]+)$', views.article, name='article'),
    re_path(r'^content$', views.content),
    re_path(r'^summary$', views.summary),
    re_path(r'^catchfish$', views.catch_fish),
    re_path(r'^ortest$', views.overlap_removal_test),
    re_path(r'^images/(?P<image>.+)$', views.image_redirect),
    re_path(r'^find-article$', views.find_article),
    re_path(r'^search$', views.search, name="search"),
    path("full.html", views.full),
]
