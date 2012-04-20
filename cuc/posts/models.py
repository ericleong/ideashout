from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.template.defaultfilters import slugify

# Create your models here.

class Post(models.Model):
    title = models.CharField(max_length=200)
    description = models.CharField(max_length=2000)
    created = models.DateTimeField(auto_now_add=True)
    link = models.CharField(max_length=300, blank=True)
    author = models.ForeignKey(User)
    tags = models.ManyToManyField('Tag', blank=True)
    location = models.ForeignKey('Location', blank=True, null=True)
    time = models.DateTimeField(blank=True, null=True)
    private = models.BooleanField(default=False)
    slug = models.SlugField(blank=True)    
    
    def __unicode__(self):
        return u'"%s" by %s on %s' % (self.title, self.author, self.created)
    
    def get_absolute_url(self):
        return "/post/%s/" % self.slug
    
    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Post, self).save(*args, **kwargs)

class Location(models.Model):
    name = models.CharField(max_length=100)
    room = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    latitude = models.FloatField()
    longitude = models.FloatField()

class UserProfile(models.Model):
    user = models.OneToOneField(User)
    bio = models.TextField(blank=True)
    
class Tag(models.Model):
    name = models.CharField(max_length=30)
    
class Response(models.Model):
    message = models.CharField(max_length=2000)
    created = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User)
    post = models.ForeignKey(Post, related_name='responses')
    
    def __unicode__(self):
        return u'"%s" by %s' % (self.message, self.author)
    
def create_profile(sender, **kw):
    """Creates a user profile for each user (if they don't have one already)."""
    user = kw["instance"]
    if kw["created"]:
        profile = UserProfile(user=user)
        profile.save()

post_save.connect(create_profile, sender=User, dispatch_uid="users-profilecreation-signal")
    
    