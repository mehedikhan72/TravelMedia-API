from django.urls import path
from api import views
from . import views


urlpatterns = [
    path('posts/', views.PostList.as_view()),
    path('posts/<int:pk>/', views.PostDetail.as_view()),
    path('user/register/', views.register_user, name="register"),
    path('users/<str:username>/posts/',
         views.UserPostList.as_view(), name='user_posts'),

    # Interactions
    path('post/<int:post_id>/like/', views.increase_likes, name="increase_likes"),
    path('post/<int:post_id>/unlike/',
         views.decrease_likes, name="decrease_likes"),
    path('post/<int:post_id>/like_status/',
         views.check_like_status, name="check_like_status"),

    path('post/<int:post_id>/comments/',
         views.CommentList.as_view(), name="comment"),
    path('post/<int:post_id>/comments/<int:pk>/',
         views.CommentDetail.as_view(), name="comment_detail"),

    # Follow/Unfollow
    path('users/<str:username>/f_data/', views.f_data, name="f_data"),
    path('users/<str:username>/follow/', views.follow, name="follow"),
    path('users/<str:username>/unfollow/', views.unfollow, name="unfollow"),

    # Images
    path('get_images/<int:post_id>/', views.get_images, name="get_images"),
    path('post_images/', views.post_images, name="post_images"),

    # Search
    path('search/users/', views.search_user, name='search_user'),

    # Notifications
    path('notifications/', views.get_notifications, name='get_notifications'),
    path('get_unseen_notifications_count/', views.get_unseen_notifications_count,
         name='get_unseen_notifications_count'),
    path('mark_notifications_as_seen/', views.mark_notifications_as_seen,
         name='mark_notifications_as_seen'),

    # Utils
    path('save_post/<int:post_id>/', views.save_post, name='save_post'),
    path('is_post_saved/<int:post_id>/',
         views.is_post_saved, name='is_post_saved'),
    path('get_saved_posts/', views.SavedPostList.as_view()),
    path('report_post/<int:post_id>/', views.report_post, name='report_post'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('get_user_data/<str:username>/',
         views.get_user_data, name='get_user_data'),
    path('report_user/<str:username>/', views.report_user, name='report_user'),
    path('get_current_user/', views.get_current_user, name='get_current_user'),
    path('add_social_image/', views.add_social_image, name='add_social_image'),
    path('get_featured_posts/', views.get_featured_posts, name='get_featured_posts'),
    path('get_following_posts/', views.get_following_posts, name='get_following_posts'),
]
