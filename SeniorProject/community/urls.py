from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
app_name = 'community'

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('profile/', views.profile, name='profile'),
    path('profile/saved/', views.profile_saved, name='profile_saved'),
    path('post/<int:post_id>/', views.post_detail, name='post_detail'),
    path('search/', views.search, name='search'),
    path('create_post/', views.create_post, name='create_post'),

    path('comment/add/<int:post_id>/', views.add_comment, name='add_comment'),
    path('comment/delete/<int:comment_id>/', views.delete_comment, name='delete_comment'),
    path('reply/add/<int:comment_id>/', views.add_reply, name='add_reply'),
    path('reply/delete/<int:reply_id>/', views.delete_reply, name='delete_reply'),
    
    #new
    path('edit_post/<int:post_id>/', views.edit_post, name='edit_post'),
    
    # Delete post URL
    path('delete_post/<int:post_id>/', views.delete_post, name='delete_post'),

    #Save Post
    path('post/<int:post_id>/save/', views.save_post, name='save_post'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)