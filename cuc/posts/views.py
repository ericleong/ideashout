# Create your views here.

from django import forms
from django.contrib.auth.models import User
from django.contrib.syndication.views import Feed
from django.forms.widgets import Textarea, TextInput
from django.http import HttpResponse
from django.shortcuts import redirect
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView
from django.views.generic.list import ListView
from icalendar.cal import Calendar, Event
from icalendar.prop import vText, vCalAddress
from posts.models import Post, Response, Tag
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

class TagView(ListView):
    template_name = "posts/post_list.html"
    
    def get_queryset(self):
        return Post.objects.order_by("-created").filter(tags__name=self.kwargs['tag'])

        
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

# Create Posts!
class LinkCreationForm(forms.ModelForm):
    link = forms.URLField(required=True)
    tags = forms.CharField(help_text="")
    
    class Meta:
        model = Post
        fields = ('title', 'description', 'link', 'tags', 'private')
        widgets = {
            'description': Textarea(attrs={'cols': 30, 'rows': 4}),
            'tags': TextInput(),
        }
    
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(LinkCreationForm, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context['tags'] = Tag.objects.all()
        return context
    
class CreateLinkView(CreateView):
    model = Post
    form_class = LinkCreationForm
    template_name = 'posts/link_form.html'

    def form_valid(self, form):
        tag_list = []
        tags = form.data["tags"].split(",")
        for tag_str in tags:
            tag, created = Tag.objects.get_or_create(name=tag_str) #@UnusedVariable
            tag_list.append(tag.pk)
        
        form.cleaned_data["tags"] = tag_list
        self.object = form.save(commit=False)
        self.object.author = self.request.user
        
        return super(CreateLinkView, self).form_valid(form)
    

class EventCreationForm(LinkCreationForm):
    class Meta:
        model = Post
        fields = ('title', 'description', 'link', 'start_time', 'end_time', 'tags', 'private')
        widgets = {
            'description': Textarea(attrs={'cols': 30, 'rows': 4}),
        }
        
    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.author = self.request.user
        super(EventCreationForm, self).form_valid(form)
        
class CreateEventView(CreateLinkView):
    model = Post
    form_class = EventCreationForm
    template_name = 'posts/event_form.html'

def api_post(request):
    return HttpResponse('hi')

def generate_calendar(request):
    """http://codespeak.net/icalendar/"""
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