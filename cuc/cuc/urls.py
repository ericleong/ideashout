from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView
from django.views.generic.list import ListView
from posts.models import Post
from posts.views import latestPostsFeed, PostCreationForm, PostCreateView, \
    PostView
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
    
    url(r'^$', ListView.as_view(model=Post, queryset=Post.objects.order_by("-created"), context_object_name="posts",)), 
    url(r'^post/(?P<slug>.+)/$', PostView.as_view(model=Post, )),
    
    url(r'^signup$', CreateView.as_view(model=User, form_class=UserCreationForm, success_url="/login"), name="signup"),
    url(r'^login$', django.contrib.auth.views.login, {'template_name': 'auth/login.html'}, name="login"),
    
    url(r'^post$', PostCreateView.as_view(success_url="/"), name="post"),
    url(r'^rss$', latestPostsFeed(), name="latest_rss"),
)
