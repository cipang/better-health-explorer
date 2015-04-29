from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'his.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', 'web.views.home', name='home'),
    url(r'^content$', 'web.views.content'),
    url(r'^summary$', 'web.views.summary'),
    url(r'^catchfish$', 'web.views.catch_fish'),
    url(r'^ortest$', 'web.views.overlap_removal_test'),
    url(r'^images/(?P<image>.+)$', 'web.views.image_redirect'),
    url(r'^find-article$', 'web.views.find_article'),
)
