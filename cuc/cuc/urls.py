from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.views.generic.edit import CreateView
from django.views.generic.list import ListView
from posts.models import Post
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
    
    url(r'^$', ListView.as_view(model=Post,)), 
    
    url(r'^signup$', CreateView.as_view(model=User, form_class=UserCreationForm, success_url="/login")),
    url(r'^login$', django.contrib.auth.views.login, {'template_name': 'auth/login.html'}),
    
    url(r'^post$', CreateView.as_view(model=Post, success_url="/post"), name="post"),
)
