from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.views.generic.base import RedirectView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView
from posts.models import Post, UserProfile
from posts.views import latestPostsFeed, PostView, generate_calendar, UserView, \
    CreateLinkView, CreateEventView, TagView, SignupForm, EditUserView
import django.contrib.auth.views
import settings

# Uncomment the next two lines to enable the admin:
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'cuc.views.home', name='home'),
    # url(r'^cuc/', include('cuc.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    
    # Posts
    url(r'^$', ListView.as_view(model=Post, queryset=Post.objects.order_by("-created"), context_object_name="posts",)), 
    url(r'^post/(?P<slug>.+)/$', PostView.as_view(model=Post, ), name="post"),
    #url(r'^post/(?P<slug>.+)/$', PostView.as_view(model=Post, )),
    
    url(r'^post/$', RedirectView.as_view(url="create/link")),
    url(r'^create/link$', CreateLinkView.as_view(success_url="/"), name="create-link"),
    url(r'^create/event$', CreateEventView.as_view(success_url="/"), name="create-event"),
    
    # Tags
    url(r'^tag/(?P<tag>.+)/$', TagView.as_view(model=Post, context_object_name="posts",), name="tag"),
    
    # Accounts
    url(r'^signup$', CreateView.as_view(model=User, form_class=SignupForm, success_url=settings.LOGIN_URL), name="signup"),
    url(r'^login$', django.contrib.auth.views.login, {'template_name': 'auth/login.html'}, name="login"),
    url(r'^user(?:s)?/(?P<slug>.+)/$', UserView.as_view(model=User, ), name="userprofile"),
    url(r'^logout$', django.contrib.auth.views.logout, name="logout"),
    url(r'^edit-profile$', EditUserView.as_view()),

    # Feeds
    url(r'^rss(?:\.rss)?$', latestPostsFeed(), name="latest_rss"),
    url(r'^ical(?:\.ics)?$', generate_calendar, name="web_calendar")
)
