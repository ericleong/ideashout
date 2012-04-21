# Create your views here.

from django import forms
from django.contrib.auth.models import User
from django.contrib.syndication.views import Feed
from django.forms.widgets import Textarea
from django.http import HttpResponse
from django.shortcuts import redirect
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView
from icalendar.cal import Calendar, Event
from icalendar.prop import vText, vCalAddress
from posts.models import Post, Response
import datetime

class latestPostsFeed(Feed):
    title = "CUES Feed"
    link = "/posts/"
    description = "Feed of posts our members think are awesome!"

    def items(self):
        return Post.objects.order_by('-created')[:10]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.description
    
    def item_link(self, item):
        if item and item.link:
            return item.link
        else:
            return ''
        
class UserView(DetailView):
    model = User
    slug_field = 'username'

class ResponseForm(forms.ModelForm):
    
    class Meta:
        model = Response
        fields = ('message', )
        widgets = {
            'message': Textarea(attrs={'cols': 40, 'rows': 3}),
        }

class PostView(DetailView):
    model = Post
    
    def post(self, request, *args, **kwargs):
        
        # TODO: fix this to be less hacky
        try:
            if request.POST:
                form = ResponseForm(request.POST)
                response = form.save(commit=False)
                response.author = request.user
                response.post = self.get_object()
                response.save()
        except:
            pass
            
        #TODO: don't redirect.
        #return super(PostView, self).post(request, *args, **kwargs)
        return redirect(self.get_object().get_absolute_url())
    
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(PostView, self).get_context_data(**kwargs)
        
        form = ResponseForm(initial={'author': self.request.user, 'post': self.object})
        
        context['comment_form'] = form
        
        return context

class PostCreationForm(forms.ModelForm):
    class Meta:
        model = Post
        exclude = ('author', 'slug')
        widgets = {
            'description': Textarea(attrs={'cols': 30, 'rows': 4}),
        }
        
    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.author = self.request.user
        super(PostCreationForm, self).form_valid(form)
        
class PostCreateView(CreateView):
    model = Post
    form_class = PostCreationForm

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.author = self.request.user
        
        return super(PostCreateView, self).form_valid(form)

def api_post(request):
    return HttpResponse('hi')

def generate_calendar(request):
    from icalendar.prop import UTC
    
    cal = Calendar()
    cal.add('prodid', '-//Club Connect//ericleong.me//')
    cal.add('version', '2.0')
    posts = Post.objects.order_by('-created')
    
    # TODO: separate out private events using a private URL?
    for post in posts:
        if post.start_time:
            # Make sure we have a time
            event = Event()
            event.add('summary', vText(post.title))
            event.add('dtstart', post.start_time)
            event.add('dtend', post.end_time if post.end_time else post.start_time)
            #event.add('dtstamp', datetime(2005,4,4,0,10,0,tzinfo=UTC))
            event['uid'] = vText(post.id)
            event['organizer'] = vText(post.author.username)
            event['description'] = vText(post.description)
            
            if post.location:
                event['location'] = vText(post.location.name)
                
            for commit in post.committed.all():
                attendee = vCalAddress('MAILTO:' + commit.email)
                name = ([commit.first_name, commit.last_name]) if (commit.first_name and commit.last_name) else commit.username;
                attendee.params['cn'] = vText(name)
                event.add('attendee', attendee, encode=0)
        
            cal.add_component(event)
    
    return HttpResponse(cal.as_string())