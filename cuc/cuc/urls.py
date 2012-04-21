from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.views.generic.base import RedirectView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView
from django.views.generic.list import ListView
from posts.models import Post, UserProfile
from posts.views import latestPostsFeed, PostView, generate_calendar, UserView, \
    CreateLinkView, CreateEventView
import django.contrib.auth.views

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
    url(r'^post/(?P<slug>.+)/$', PostView.as_view(model=Post, ), "post"),
    
    url(r'^post/', RedirectView.as_view(url='/create/link')),
    url(r'^create/link$', CreateLinkView.as_view(success_url="/"), name="create-link"),
    url(r'^create/event$', CreateEventView.as_view(success_url="/"), name="create-event"),
    
    # Accounts
    url(r'^signup$', CreateView.as_view(model=User, form_class=UserCreationForm, success_url="/login"), name="signup"),
    url(r'^login$', django.contrib.auth.views.login, {'template_name': 'auth/login.html'}, name="login"),
    url(r'^user/(?P<slug>.+)/$', UserView.as_view(model=User, ), name="userprofile"),

    # Feeds
    url(r'^rss$', latestPostsFeed(), name="latest_rss"),
    url(r'^ical(?:\.ics)?$', generate_calendar, name="web_calendar")
)
