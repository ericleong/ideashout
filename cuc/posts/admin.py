'''
Created on Apr 20, 2012

@author: Eric
'''
from django.contrib import admin
from posts.models import Post, Response, Location

class PostAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}
    
class ResponseAdmin(admin.ModelAdmin):
    pass

class LocationAdmin(admin.ModelAdmin):
    pass

admin.site.register(Post, PostAdmin)
admin.site.register(Response, ResponseAdmin)
admin.site.register(Location, LocationAdmin)