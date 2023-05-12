from django.db import models
import datetime
from django.contrib.auth.models import AbstractUser

# Create your models here.


class User(AbstractUser):
    first_name = models.CharField(max_length=256, blank=True)
    last_name = models.CharField(max_length=256, blank=True)
    gender = models.CharField(default="Male", max_length=28)
    location = models.CharField(max_length=256, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    bio = models.CharField(max_length=256, blank=True)
    followers = models.ManyToManyField(
        'self', blank=True, related_name="following", symmetrical=False)
    pfp = models.ImageField(null=True, blank=True, upload_to="img")
    social_pfp_link = models.CharField(max_length=256, blank=True)

    # Other data like number of trip reviewed, exp level n others will be implemented later.
    trips_reviewed = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.username}"


class Post(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE, default=None)
    post = models.TextField(default="")
    place = models.CharField(max_length=256, default="")
    trip_date = models.DateField(default=datetime.date.today)
    trip_duration = models.PositiveIntegerField(default=0)
    people_count = models.PositiveIntegerField(default=0)
    cost_per_person = models.PositiveIntegerField(default=0)
    transportation_data = models.TextField(default="")
    staying_place = models.CharField(default="", max_length=256)
    staying_place_cost = models.PositiveIntegerField(default=0)
    staying_place_rating = models.FloatField(default=0.0)
    trip_rating = models.FloatField(default=0.0)
    important_things_to_take = models.TextField(default="", blank=True)
    cautions = models.TextField(default="", blank=True)
    featured_image = models.ImageField(null=True, blank=True, upload_to="img")
    
    # RELEVANCE SCORE
    # one like 5 pts
    # one dislike -5 pts
    # one comment 10 pts
    # one save 5 pts

    # Interactions
    likes = models.ManyToManyField(
        User, blank=True, related_name="users_who_like")
    dislikes = models.ManyToManyField(
        User, blank=True, related_name="users_who_dislike")

    def __str__(self):
        return f"{self.creator} posted {self.post} on {self.trip_date}"

class PostImages(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    image = models.ImageField(
        null=True, blank=True, upload_to="img")

    def __str__(self):
        return f"{self.post}"


class Comment(models.Model):
    comment_text = models.TextField()
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    created_time = models.DateTimeField(auto_now_add=True)
    post = models.ForeignKey(
        'Post', on_delete=models.CASCADE, related_name='comments')

    def __str__(self):
        return f"{self.comment_text} by {self.creator} on {self.post}"


class SavedPost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user} saved {self.post}"


class ReportPost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    reason = models.TextField()
    date = models.DateField(default=datetime.date.today)

    def __str__(self):
        return f"{self.user} reported {self.post} for {self.reason}"


class ReportUser(models.Model):
    reporting_user = models.ForeignKey(User, on_delete=models.CASCADE)
    reported_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="reported_user")
    reason = models.TextField()
    date = models.DateField(default=datetime.date.today)

    def __str__(self):
        return f"{self.reporting_user} reported {self.reported_user} for {self.reason}"
    
class Notification(models.Model):
    receiving_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="receiving_user")
    sending_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sending_user")
    sender_pfp_url = models.CharField(max_length=256, default="", null=True, blank=True)
    related_post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="related_post", null=True, blank=True)
    notification_type = models.CharField(max_length=256)
    notification_text = models.TextField()
    date = models.DateField(default=datetime.date.today)
    seen = models.BooleanField(default=False)
    sender_social_pfp_link = models.CharField(max_length=256, default="", null=True, blank=True)

    def __str__(self):
        return f"{self.receiving_user} received notification from {self.sending_user}"
