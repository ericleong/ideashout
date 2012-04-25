from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.auth.models import User
from django.views.generic.base import RedirectView
from django.views.generic.edit import CreateView
from django.views.generic.list import ListView
from posts.models import Post
from posts.views import latestPostsFeed, PostView, generate_calendar, UserView, \
    CreateLinkView, CreateEventView, TagView, SignupForm, EditUserView, \
    CreateIdeaView
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
    url(r'^$', ListView.as_view(model=Post, queryset=Post.objects.order_by("-created"), context_object_name="posts",), name="home"),
    url(r'^events$', ListView.as_view(model=Post, queryset=Post.objects.filter(start_time__isnull=False).order_by("start_time"), 
                                template_name="posts/event_list.html", context_object_name="posts",), name="events"),
    url(r'^links$', ListView.as_view(model=Post, queryset=Post.objects.filter(start_time__isnull=True, link__isnull=False).order_by("-created"), 
                                template_name="posts/link_list.html", context_object_name="posts",), name="links"),
    url(r'^ideas$', ListView.as_view(model=Post, queryset=Post.objects.filter(start_time__isnull=True, link__isnull=True).order_by("-responses__created"), 
                                template_name="posts/idea_list.html", context_object_name="posts",), name="ideas"), 
    url(r'^post/(?P<slug>.+)/$', PostView.as_view(model=Post, ), name="post"),
    #url(r'^post/(?P<slug>.+)/$', PostView.as_view(model=Post, )),
    
    url(r'^post/$', RedirectView.as_view(url="create/link")),
    url(r'^create/idea$', CreateIdeaView.as_view(success_url="/"), name="create-idea"),
    url(r'^create/link$', CreateLinkView.as_view(success_url="/"), name="create-link"),
    url(r'^create/event$', CreateEventView.as_view(success_url="/"), name="create-event"),
    
    # Tags
    url(r'^tag/(?P<tag>.+)/$', TagView.as_view(model=Post, context_object_name="posts",), name="tag"),
    
    # Accounts
    url(r'^signup$', CreateView.as_view(model=User, form_class=SignupForm, success_url=settings.LOGIN_URL), name="signup"),
    url(r'^login$', django.contrib.auth.views.login, name="login"),
    url(r'^user(?:s)?/(?P<slug>.+)/$', UserView.as_view(model=User, context_object_name="member"), name="userprofile"),
    url(r'^logout$', django.contrib.auth.views.logout_then_login, name="logout"),
    url(r'^edit-profile$', EditUserView.as_view(), name="edit-profile"),
    url(r'^directory$', ListView.as_view(model=User, queryset=User.objects.order_by("last_name"), context_object_name="users",), name="directory"),

    # Feeds
    url(r'^rss(?:\.rss)?$', latestPostsFeed(), name="latest_rss"),
    url(r'^ical(?:\.ics)?$', generate_calendar, name="web_calendar")
)
