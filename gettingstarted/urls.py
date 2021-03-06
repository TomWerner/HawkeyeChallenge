from django.conf.urls import include, url

from django.contrib import admin
admin.autodiscover()

from minos.views import views, question_views

from django.conf import settings
from django.conf.urls.static import static

# Examples:
# url(r'^$', 'gettingstarted.views.home', name='home'),
# url(r'^blog/', include('blog.urls')),

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/login/$', 'django.contrib.auth.views.login'),  # If user is not login it will redirect to login page
    url(r'^login/', views.login_view, name='login'),
    url(r'^logout/', views.logout_view, name='logout'),
    url(r'^$', views.index, name='index'),
    url(r'^rules', views.rules, name='rules'),
    url(r'^questions', question_views.questions, name='questions'),
    url(r'^question/([0-9]+)$', question_views.question_view, name='question_view'),
    url(r'^question/([0-9]+)/submit', question_views.submit_question, name='submit_question'),
    url(r'^customTestCase', question_views.custom_test_case, name='custom_test_case'),
    url(r'^starterCode', question_views.get_starter_code, name='get_starter_code'),
    url(r'^leaderboard', views.leaderboard, name='leaderboard'),
    url(r'^clarify', views.clarify, name='clarify'),
    url(r'^add_clarification_answer', views.add_clarification_answer, name='add_clarification_answer'),
    url(r'^clarification_request/([0-9]+)', views.add_clarification_request, name='add_clarification_request'),
    url(r'^pickContest/([0-9]+)$', views.pick_contest, name='pick_contest'),
] #+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
