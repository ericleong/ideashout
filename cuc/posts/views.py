# Create your views here.

from django import forms
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.syndication.views import Feed
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.forms.widgets import Textarea, TextInput
from django.http import HttpResponse
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView
from icalendar.cal import Calendar, Event
from icalendar.prop import vText, vCalAddress, vUri
from posts.models import Post, Response, Tag, Location

class TagView(ListView):
    # TODO: a slightly different page with the tag name?
    template_name = "posts/post_list.html"
    
    def get_queryset(self):
        return Post.objects.order_by("-created").filter(tags__name=self.kwargs['tag'])


class UserView(DetailView):
    model = User
    slug_field = 'username'

class EditUserForm(forms.ModelForm):
    bio = forms.CharField(widget = Textarea(attrs={'cols': 40, 'rows': 3}))
    
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'bio')

class EditUserView(UpdateView):
    model = User
    form_class = EditUserForm
    template_name = "auth/user_edit_form.html"
    
    def get_object(self):
        return self.request.user
    
    def get_initial(self):
        return {'bio': self.request.user.get_profile().bio }
    
    def form_valid(self, form):
        profile = self.request.user.get_profile()
        profile.bio = form.cleaned_data["bio"]
        profile.save()
        
        return super(EditUserView, self).form_valid(form)
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(EditUserView, self).dispatch(*args, **kwargs)
    
class SignupForm(UserCreationForm):
    
    email = forms.EmailField(help_text="'cooper.edu' email required.")
    
    def clean_email(self):
        email = self.cleaned_data['email']
        if len(email) < 10 or email[-10:] != 'cooper.edu':
            raise ValidationError("You need a 'cooper.edu' email address to sign up.")
        
        return email
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')
        
class CommitForm(forms.Form):
    commit = forms.BooleanField(widget=forms.HiddenInput)        

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
        if request.POST:
            comment_form = ResponseForm(request.POST)
            if comment_form.is_valid():            
                response = comment_form.save(commit=False)
                response.author = request.user
                response.post = self.get_object()
                response.save()
            else:
                commit_form = CommitForm(request.POST)
                
                post = self.get_object()
                if 'commit' in commit_form.data:
                    if commit_form.data['commit'] == "True":   
                        post.committed.add(self.request.user)
                    else:
                        post.committed.remove(self.request.user)
            
        #TODO: don't redirect.
        #return super(PostView, self).post(request, *args, **kwargs)
        return redirect(self.get_object().get_absolute_url())
    
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(PostView, self).get_context_data(**kwargs)
        
        comment_form = ResponseForm(initial={'author': self.request.user, 'post': self.object})
        commit_form = CommitForm(initial={'commit': not self.object.committed.filter(id=self.request.user.id).exists()})
        
        context['comment_form'] = comment_form
        context['commit_form'] = commit_form
        
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
        
    def clean_tags(self):
        tag_list = []
        tags = self.cleaned_data["tags"].split(",")
        for tag_str in tags:
            tag, created = Tag.objects.get_or_create(name=tag_str) #@UnusedVariable
            tag_list.append(tag.pk)
        
        return tag_list
    
class CreateLinkView(CreateView):
    model = Post
    form_class = LinkCreationForm
    template_name = 'posts/link_form.html'
    
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(CreateLinkView, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the tags
        context['tags'] = Tag.objects.all()
        return context
    
    def form_valid(self, form):
        form.cleaned_data["author"] = self.request.user
        
        self.object = form.save(commit=False)
        self.object.author = self.request.user
        
        return super(CreateLinkView, self).form_valid(form)
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(CreateLinkView, self).dispatch(*args, **kwargs)

class IdeaCreationForm(forms.ModelForm):
    tags = forms.CharField(help_text="")
    
    class Meta:
        model = Post
        fields = ('title', 'description', 'tags', 'private')
        widgets = {
            'description': Textarea(attrs={'cols': 30, 'rows': 4}),
            'tags': TextInput(),
        }
        
    def clean_tags(self):
        tag_list = []
        tags = self.cleaned_data["tags"].split(",")
        for tag_str in tags:
            tag, created = Tag.objects.get_or_create(name=tag_str.lower()) #@UnusedVariable
            tag_list.append(tag.pk)
        
        return tag_list

class CreateIdeaView(CreateLinkView):
    model = Post
    form_class = IdeaCreationForm
    template_name = 'posts/idea_form.html'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(CreateIdeaView, self).dispatch(*args, **kwargs)

class EventCreationForm(LinkCreationForm):
    location = forms.CharField(max_length=100)
    room = forms.CharField(max_length=100, required=False, label='Room/Floor (specify)')
    address = forms.CharField(max_length=200)
    link = forms.URLField(required=False)
    
    class Meta:
        model = Post
        fields = ('title', 'description', 'link', 'location', 'room', 'address', 'start_time', 'end_time', 'tags', 'private')
        widgets = {
            'description': Textarea(attrs={'cols': 30, 'rows': 4}),
        }
    
    def clean_location(self):
        loc_str = self.cleaned_data["location"]
        room_str = self.data["room"]
        address_str = self.data["address"]
        
        location, created = Location.objects.get_or_create(name=loc_str, #@UnusedVariable
                                                           room=room_str, 
                                                           address=address_str)
        
        return location
        
class CreateEventView(CreateLinkView):
    model = Post
    form_class = EventCreationForm
    template_name = 'posts/event_form.html'
    
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(CreateEventView, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the locations
        context['locations'] = Location.objects.all()
        return context
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(CreateEventView, self).dispatch(*args, **kwargs)
    

class latestPostsFeed(Feed):
    title = "Club Connect Posts"
    link = "/posts/"
    description = "Feed of posts our members think are awesome!"

    def items(self):
        return Post.objects.order_by('-created')[:10]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.description
    
    def item_pubdate(self, item):
        return item.created
    
    def item_categories(self, item):
        return [tag.name for tag in item.tags.all()]
    
    def item_guid(self, item):
        return item.get_absolute_url()
    
    def item_author_name(self, item):
        return item.author.username
    
    def item_author_email(self, item):
        return item.author.email
    
    def item_author_link(self, item):
        return reverse('userprofile', args=[item.author])
    
    def item_link(self, item):
        return item.get_absolute_url()

def generate_calendar(request):
    """http://codespeak.net/icalendar/"""
    
    cal = Calendar()
    cal.add('prodid', '-//Club Connect//ericleong.me//')
    cal.add('version', '2.0')
    posts = Post.objects.order_by('-created')
    
    cal['X-WR-CALNAME'] = 'Club Connect Events'
    cal['X-PUBLISH-TTL'] = 'PT12H'
    cal['CALSCALE'] = 'GREGORIAN'
    cal['METHOD'] = 'PUBLISH'
    
    # TODO: separate out private events using a private URL?
    # TODO: switch to using EDT
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
            event['url'] = vUri(post.get_absolute_url())
            
            if post.location:
                if post.location.room:
                    event['location'] = vText('%s (%s)' % (post.location.name, post.location.room))
                else:
                    event['location'] = vText(post.location.name) 
                
            for commit in post.committed.all():
                attendee = vCalAddress('MAILTO:' + commit.email)
                name = ([commit.first_name, commit.last_name]) if (commit.first_name and commit.last_name) else commit.username;
                attendee.params['cn'] = vText(name)
                event.add('attendee', attendee, encode=0)
        
            cal.add_component(event)
    
    return HttpResponse(cal.to_ical().replace('\n', '\r\n'), content_type="text/calendar")