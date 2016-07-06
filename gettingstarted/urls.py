from django.conf.urls import include, url

from django.contrib import admin
admin.autodiscover()

import minos.views

# Examples:
# url(r'^$', 'gettingstarted.views.home', name='home'),
# url(r'^blog/', include('blog.urls')),

urlpatterns = [
    url(r'^$', minos.views.index, name='index'),
    url(r'^db', minos.views.db, name='db'),
    url(r'^admin/', include(admin.site.urls)),
]
