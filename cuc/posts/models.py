from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save

# Create your models here.

class Post(models.Model):
    title = models.CharField(max_length=200)
    description = models.CharField(max_length=2000)
    time = models.DateTimeField(auto_now_add=True)
    poster = models.ForeignKey(User)
    
    def __unicode__(self):
        return u'"%s" by %s' % (self.title, self.poster)

class UserProfile(models.Model):
    user = models.OneToOneField(User)
    bio = models.TextField(blank=True)
    
class Tag(models.Model):
    name = models.CharField(max_length=30)
    
class Comment(models.Model):
    message = models.CharField(max_length=2000)
    time = models.DateTimeField(auto_now_add=True)
    commenter = models.ForeignKey(User)
    
    def __unicode__(self):
        return u'"%s" by %s' % (self.message, self.poster)
    
def create_profile(sender, **kw):
    """Creates a user profile for each user (if they don't have one already)."""
    user = kw["instance"]
    if kw["created"]:
        profile = UserProfile(user=user)
        profile.save()

post_save.connect(create_profile, sender=User, dispatch_uid="users-profilecreation-signal")
    
    