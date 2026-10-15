from django.contrib import admin
from .models import ChaiMessage, ChaiRoom, Comment, Follow, Like, Tweet
# Register your models here.

admin.site.register(Tweet)
admin.site.register((Like, Comment, Follow))


admin.site.register((ChaiRoom, ChaiMessage))
