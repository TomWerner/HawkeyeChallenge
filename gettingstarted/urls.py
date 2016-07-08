from django.conf.urls import include, url

from django.contrib import admin
admin.autodiscover()

import minos.views

# Examples:
# url(r'^$', 'gettingstarted.views.home', name='home'),
# url(r'^blog/', include('blog.urls')),

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/login/$', 'django.contrib.auth.views.login'),  # If user is not login it will redirect to login page
    url(r'^login/', minos.views.login_view, name='login'),
    url(r'^logout/', minos.views.logout_view, name='logout'),
    url(r'^$', minos.views.index, name='index'),
    url(r'^rules', minos.views.rules, name='rules'),
    url(r'^questions', minos.views.questions, name='questions'),
    url(r'^leaderboard', minos.views.leaderboard, name='leaderboard'),
    url(r'^clarify', minos.views.clarify, name='clarify'),
]
