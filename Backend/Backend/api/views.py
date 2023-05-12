from django.db import IntegrityError
from django.db.models import Q
from .serializers import CurrentUserSerializer
import json
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth import get_user_model
from django.forms.models import model_to_dict
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.shortcuts import render, get_object_or_404
from .models import Post, User, Comment, PostImages, SavedPost, ReportPost, ReportUser, Notification
from .serializers import PostSerializer, UserRegisterSerializer, CommentSerializer, ImageSerializer, UserSerializer, SavedPostSerializer, NotificationSerializer
from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.http import JsonResponse

# Create your views here.


class PostList(generics.ListCreateAPIView):
    queryset = Post.objects.all().order_by('-id')
    serializer_class = PostSerializer

    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            serializer.save(creator=self.request.user)
        else:
            raise ValueError("User must be authenticated to create a post.")

    def get_queryset(self):
        qs = Post.objects.all().order_by('-id')
        search_term = self.request.query_params.get('query', None)
        if search_term is not None:
            qs = qs.filter(
                Q(place__icontains=search_term) |
                Q(post__icontains=search_term) |
                Q(creator__username__icontains=search_term) |
                Q(creator__first_name__icontains=search_term) |
                Q(creator__last_name__icontains=search_term)
            )
        return qs


class PostDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class SavedPostList(generics.ListAPIView):
    serializer_class = SavedPostSerializer

    def get_queryset(self):
        user = self.request.user
        qs = SavedPost.objects.filter(user=user).order_by('-id')
        return qs


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_user(request):
    search_term = request.query_params.get('query', None)
    if search_term is not None:
        qs = User.objects.filter(
            Q(username__icontains=search_term) |
            Q(first_name__icontains=search_term) |
            Q(last_name__icontains=search_term)
        )
        serializer = UserSerializer(qs, many=True)
        return JsonResponse(serializer.data, safe=False)

    return JsonResponse({'error': 'No search term provided'}, status=status.HTTP_400_BAD_REQUEST)


class UserPostList(generics.ListCreateAPIView):
    serializer_class = PostSerializer

    def get_queryset(self):
        username = self.kwargs['username']
        user = get_object_or_404(User, username=username)
        queryset = Post.objects.filter(creator=user).order_by('-id')
        return queryset


@api_view(['POST'])
def register_user(request):
    serializer = UserRegisterSerializer(data=request.data)
    if serializer.is_valid():
        username = serializer.validated_data['username']
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        if len(password) < 8:
            return Response({'error': 'Password must be at least 8 characters'}, status=status.HTTP_400_BAD_REQUEST)
        if not email or not username or not password:
            return Response({'error': 'Please provide all fields'}, status=status.HTTP_400_BAD_REQUEST)

        User.objects.create_user(
            username=username, email=email, password=password)
        return Response(serializer.validated_data, status=status.HTTP_201_CREATED)

    error = serializer.errors['username'][0]
    if error:
        return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)
    error = serializer.errors['email'][0]
    if error:
        return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

    return Response({'error': 'Unknown error occured. Please try again.'}, status=status.HTTP_400_BAD_REQUEST)


@receiver(post_save, sender=Notification)
def send_notification(sender, instance, created, **kwargs):
    if created:
        channel_layer = get_channel_layer()
        post_owner = instance.receiving_user.id
        sender_pfp = instance.sending_user.pfp
        if (sender_pfp):
            sender_pfp_url = sender_pfp.url
        else:
            sender_pfp_url = None

        group_name = f"notification-{post_owner}"
        if instance.related_post:
            related_post = instance.related_post.id
        else:
            related_post = None

        sending_user = UserSerializer(instance.sending_user)

        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                "type": "send_notification",
                "notification": json.dumps({
                    "id": instance.id,
                    "receiving_user": instance.receiving_user.username,
                    "sending_user": sending_user.data,
                    "related_post": related_post,
                    "notification_type": instance.notification_type,
                    "notification_text": instance.notification_text,
                    "date": instance.date.isoformat(),
                    "seen": instance.seen,
                    "sender_pfp_url": sender_pfp_url,
                    "sender_social_pfp_link": instance.sending_user.social_pfp_link,
                })
            }
        )

# USER INTERACTION VIEWS


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def increase_likes(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    user = request.user
    # Access the creator of the post
    post_creator = post.creator

    # Add notification
    if user != post_creator and user not in post.likes.all():
        if user.first_name:
            notification_text = f"{user.first_name} {user.last_name} upvoted your post."
        else:
            notification_text = f"{user.username} upvoted your post."
        sender_pfp = user.pfp
        if (sender_pfp):
            sender_pfp_url = sender_pfp.url
        else:
            sender_pfp_url = None
        notification = Notification.objects.create(
            receiving_user=post_creator, sending_user=user, sender_pfp_url=sender_pfp_url, sender_social_pfp_link=user.social_pfp_link, related_post=post, notification_text=notification_text, notification_type='upvote', seen=False)
        notification.save()

    if user in post.likes.all():
        post.likes.remove(user)
        post.save()

        return JsonResponse({})
    if user in post.dislikes.all():
        post.dislikes.remove(user)
        post.likes.add(user)
        post.save()

        return JsonResponse({})

    post.likes.add(user)
    post.save()

    return JsonResponse({})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def decrease_likes(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    user = request.user
    if user in post.dislikes.all():
        post.dislikes.remove(user)
        post.save()

        return JsonResponse({})
    if user in post.likes.all():
        post.likes.remove(user)
        post.dislikes.add(user)
        post.save()

        return JsonResponse({})

    post.dislikes.add(user)
    post.save()

    return JsonResponse({})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_like_status(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    likes_count = post.likes.all().count() - (post.dislikes.all().count())
    user = request.user
    if user in post.likes.all():
        status = 'liked'
    elif user in post.dislikes.all():
        status = 'disliked'
    else:
        status = 'not-interacted'
    return JsonResponse({
        'status': status,
        'likes_count': likes_count
    })


class CommentList(generics.ListCreateAPIView):
    pagination_class = None
    serializer_class = CommentSerializer

    def get_queryset(self):
        post_id = self.kwargs['post_id']
        queryset = Comment.objects.filter(post_id=post_id).order_by('-id')
        return queryset

    def perform_create(self, serializer):
        post_id = self.kwargs['post_id']
        serializer.save(creator=self.request.user, post_id=post_id)

        # Add notification
        post = Post.objects.get(id=post_id)
        post_creator = post.creator
        if self.request.user != post_creator:
            if self.request.user.first_name:
                notification_text = f"{self.request.user.first_name} {self.request.user.last_name} commented on your post."
            else:
                notification_text = f"{self.request.user.username} commented on your post."

            sender_pfp = self.request.user.pfp
            if (sender_pfp):
                sender_pfp_url = sender_pfp.url
            else:
                sender_pfp_url = None

            notification = Notification.objects.create(
                receiving_user=post_creator, sending_user=self.request.user, sender_pfp_url=sender_pfp_url, sender_social_pfp_link=self.request.user.social_pfp_link, related_post=post, notification_text=notification_text, notification_type='comment', seen=False)
            notification.save()


class CommentDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer


# FOLLOW/UNFOLLOW
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def follow(request, username):
    user = User.objects.get(username=username)
    if request.user != user and not request.user.following.filter(pk=user.pk).exists():
        request.user.following.add(user)
        if request.user.first_name:
            notification_text = f'{request.user.first_name} {request.user.last_name} started following you.'
        else:
            notification_text = f'{request.user.username} started following you.'

        sender_pfp = request.user.pfp
        if (sender_pfp):
            sender_pfp_url = sender_pfp.url
        else:
            sender_pfp_url = None

        notification = Notification.objects.create(
            receiving_user=user, sending_user=request.user, sender_social_pfp_link=request.user.social_pfp_link, sender_pfp_url=sender_pfp_url, notification_type='follow', notification_text=notification_text, seen=False)
        notification.save()

    return JsonResponse({})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def unfollow(request, username):
    user = User.objects.get(username=username)
    if request.user != user and request.user.following.filter(pk=user.pk).exists():
        request.user.following.remove(user)
    return JsonResponse({})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def f_data(request, username):
    user = get_object_or_404(User, username=username)
    is_following = request.user.following.filter(pk=user.pk).exists()
    followers_count = user.followers.count()
    following_count = user.following.count()
    context = {
        'is_following': is_following,
        'followers_count': followers_count,
        'following_count': following_count,
    }

    return JsonResponse(context)

# Dealing with images


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def post_images(request):
    if request.method == "POST":
        post = Post.objects.filter(creator=request.user).order_by('-id')[0]
        # print(request.user)
        # print(post)
        if (request.user != post.creator):
            return JsonResponse({
                "Error": "You are not the author of this post."
            })

        images = request.FILES.getlist('images')

        if not images:
            return JsonResponse({
                "Error": "No images were found."
            })

        if (len(images) >= 10):
            return JsonResponse({
                "Error": "More than 10 images is not allowed."
            })

        for image in images:
            post_image = PostImages.objects.create(post=post, image=image)
            print("image added")
            post_image.save()

        if images:
            post.featured_image = images[0]
            post.save()

    return JsonResponse({})


@api_view(["GET"])
def get_images(request, post_id):
    if (request.method == "GET"):
        post = Post.objects.get(id=post_id)
        images = PostImages.objects.filter(post=post)
        serializer = ImageSerializer(images, many=True)
        return JsonResponse(serializer.data, safe=False)

    return JsonResponse({})

# Save posts


@api_view(["POST"])
def save_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    user = request.user
    saved_post, created = SavedPost.objects.get_or_create(user=user, post=post)
    if not created:
        saved_post.delete()
        return JsonResponse({
            "message": "Post removed from saved posts."
        })

    return JsonResponse({
        "message": "Post saved."
    })


@api_view(["GET"])
def get_saved_posts(request):
    user = request.user
    saved_posts = SavedPost.objects.filter(user=user)
    serializer = PostSerializer(saved_posts, many=True)
    return JsonResponse(serializer.data, safe=False)


@api_view(["GET"])
def is_post_saved(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    user = request.user
    saved_post = SavedPost.objects.filter(user=user, post=post)
    if saved_post:
        message = "Saved"
    else:
        message = "Not saved"

    return JsonResponse({
        'message': message
    })


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def report_post(request, post_id):
    user = request.user
    post = get_object_or_404(Post, id=post_id)
    reason = request.data['reason']

    report = ReportPost.objects.filter(user=user, post=post)
    if report:
        return JsonResponse({
            "message": "You have already reported this post."
        })

    else:
        report = ReportPost.objects.create(user=user, post=post, reason=reason)
        report.save()
        return JsonResponse({
            "message": "Post reported."
        })


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def edit_profile(request):
    user = request.user
    if request.data.get('first_name'):
        user.first_name = request.data['first_name']

    if request.data.get('last_name'):
        user.last_name = request.data['last_name']

    if request.data.get('gender'):
        user.gender = request.data['gender']

    if request.data.get('location'):
        user.location = request.data['location']

    if request.data.get('phone_number'):
        user.phone_number = request.data['phone_number']

    if request.data.get('bio'):
        user.bio = request.data['bio']

    if request.FILES.get('pfp'):
        user.pfp = request.FILES.get('pfp')

    # update user
    user.save()

    # Return serialized user data using userSerializer
    serializer = UserSerializer(user)
    return JsonResponse(serializer.data)


@api_view(["GET"])
def get_user_data(request, username):
    user = get_object_or_404(User, username=username)
    serializer = UserSerializer(user)
    return JsonResponse(serializer.data)


@api_view(['POST'])
def report_user(request, username):
    reporting_user = request.user
    reported_user = get_object_or_404(User, username=username)
    reason = request.data['reason']

    report = ReportUser.objects.filter(
        reporting_user=reporting_user, reported_user=reported_user)
    if report:
        return JsonResponse({
            "message": "You have already reported this user."
        })

    if reason and reported_user and reporting_user:
        report = ReportUser.objects.create(
            reporting_user=reporting_user, reported_user=reported_user, reason=reason)
        report.save()

        return JsonResponse({
            "message": "User reported. We will review shortly."
        })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_notifications(request):
    user = request.user
    notifications = Notification.objects.filter(
        receiving_user=user).order_by('-id')[:50]
    serializer = NotificationSerializer(notifications, many=True)

    return JsonResponse(serializer.data, safe=False)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_unseen_notifications_count(request):
    user = request.user
    notifications = Notification.objects.filter(
        receiving_user=user, seen=False)
    count = notifications.count()
    return JsonResponse({
        'count': count
    })


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def mark_notifications_as_seen(request):
    user = request.user
    notifications = Notification.objects.filter(
        receiving_user=user, seen=False)
    for notification in notifications:
        notification.seen = True
        notification.save()

    return JsonResponse({
        'message': 'Notifications marked as seen.'
    })


# Gets the current user for AuthContext
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_current_user(request):
    user = request.user
    serializer = CurrentUserSerializer(user)
    return JsonResponse(serializer.data, safe=False)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def add_social_image(request):
    user = request.user
    user.social_pfp_link = request.data['pfp']
    user.save()
    return JsonResponse({
        'message': 'Image added.'
    })

# Relevance score algorithm


def get_score(post_id):
    post = get_object_or_404(Post, id=post_id)

    likes_count = post.likes.all().count() - post.dislikes.all().count()
    comments_count = Comment.objects.filter(post=post).all().count()
    saved_count = SavedPost.objects.filter(post=post).all().count()
    report_count = ReportPost.objects.filter(post=post).all().count()
    user = post.creator
    followers_count = user.followers.all().count()

    score = likes_count * 5 + comments_count * 10 + \
        saved_count * 5 - report_count * 20 + followers_count * 2
    return score


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_featured_posts(request):
    posts = Post.objects.all()
    posts = sorted(posts, key=lambda post: get_score(
        post.id), reverse=True)[:5]
    top_5_posts = []

    # Featured post must have at least 1 image
    for post in posts:
        if post.featured_image:
            top_5_posts.append(post)

    serializer = PostSerializer(top_5_posts, many=True)
    return JsonResponse(serializer.data, safe=False)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_following_posts(request):
    user = request.user
    following = user.following.all()
    posts = Post.objects.filter(creator__in=following).order_by('-id')
    serializer = PostSerializer(posts, many=True)
    return JsonResponse(serializer.data, safe=False)
