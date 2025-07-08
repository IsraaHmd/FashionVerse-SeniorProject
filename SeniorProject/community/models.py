from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError

class Category(models.Model):
    name = models.CharField(max_length=200, unique=True, blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Post(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='posts',
        blank=False, null=False
    )
    title = models.CharField(max_length=255, blank=False, null=False)
    # Image can be either uploaded or from an external URL
    image_upload = models.ImageField(upload_to='post_images/', blank=True, null=True)
    image_url = models.URLField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey(
        Category, 
        on_delete=models.SET_NULL, 
        related_name='posts',
        blank=True, 
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    hide = models.BooleanField(default=False)
    allow_comments = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-created_at']  # Most recent posts first
    
    def __str__(self):
        return f"{self.title} - by {self.user.username}"
    
    def get_image(self):
        """Returns the correct image URL to use in templates."""
        if self.image_url:
            return self.image_url
        elif self.image_upload and hasattr(self.image_upload, 'url'):
            return self.image_upload.url
        return ""
        
    def clean(self):
        # Check title is not just whitespace
        if not self.title.strip():
            raise ValidationError({'title': "Title cannot be blank."})
            
        # Ensure at least one form of image is provided
        if not self.image_url and not self.image_upload:
            raise ValidationError({'image_upload': "Post must have either an uploaded image or an image URL."})
        
        # If both image_url and image_upload are provided, prioritize upload remove url
        if self.image_url and self.image_upload:
            self.image_url = None

class Comment(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='comments'
    )
    post = models.ForeignKey(
        Post, 
        on_delete=models.CASCADE,
        related_name='comments'
    )
    text = models.TextField(blank=False, null=False)
    added_at = models.DateTimeField(auto_now_add=True)
    hide = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-added_at']  # Most recent comments first
    
    def __str__(self):
        return f"Comment by {self.user.username} on {self.post.title}"
    def clean(self):
            # Check if comments are allowed on this post
            if not self.post.allow_comments:
                raise ValidationError({'post': "Comments are not allowed on this post."})
            
            # Ensure comment text is not just whitespace
            if not self.text.strip():
                raise ValidationError({'text': "Comment text cannot be empty."})
class Reply(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='replies'
    )
    comment = models.ForeignKey(
        Comment, 
        on_delete=models.CASCADE,
        related_name='replies'
    )
    text = models.TextField(blank=False, null=False)
    added_at = models.DateTimeField(auto_now_add=True)
    hide = models.BooleanField(default=False)
    
    class Meta:
        verbose_name_plural = "Replies"
        ordering = ['added_at']  # Chronological order for replies
    
    def __str__(self):
        return f"Reply by {self.user.username} to {self.comment.user.username}'s comment"
    def clean(self):
        # Ensure reply text is not just whitespace
        if not self.text.strip():
            raise ValidationError({'text': "Reply text cannot be empty."})
        
        # Check if the parent post allows comments (and thus replies)
        if not self.comment.post.allow_comments:
            raise ValidationError({'comment': "Comments and replies are not allowed on this post."})
        
class Saved(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='saved_posts'
    )
    post = models.ForeignKey(
        Post, 
        on_delete=models.CASCADE,
        related_name='saved_by'
    )
    saved_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'post')  # User can save a post only once
        verbose_name_plural = "Saved Posts"
        ordering = ['-saved_at']  # Most recently saved first
    
    def __str__(self):
        return f"{self.user.username} saved {self.post.title}"