from django.contrib import admin
from .models import Post, User, Comment, PostImages, SavedPost, ReportPost, ReportUser, Notification
# Register your models here.

admin.site.register(Post)
admin.site.register(User)
admin.site.register(Comment)
admin.site.register(PostImages)
admin.site.register(SavedPost)
admin.site.register(ReportPost)
admin.site.register(ReportUser)
admin.site.register(Notification)