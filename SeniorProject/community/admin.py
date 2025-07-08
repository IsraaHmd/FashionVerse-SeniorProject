from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Post, Comment, Reply, Saved


# Inline for Comments to show within Post admin
class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    fields = ('user', 'text', 'hide', 'added_at')
    readonly_fields = ('added_at',)
    can_delete = True


# Inline for Replies to show within Comment admin
class ReplyInline(admin.TabularInline):
    model = Reply
    extra = 0
    fields = ('user', 'text', 'hide', 'added_at')
    readonly_fields = ('added_at',)
    can_delete = True


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'post_count', 'created_at')
    search_fields = ('name',)
    list_filter = ('created_at',)
    ordering = ('name',)  # Default ordering
    
    def post_count(self, obj):
        return obj.posts.count()
    post_count.short_description = 'Number of Posts'


class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'has_image', 'hidden_status', 'comments_enabled', 'created_at')
    list_filter = ('hide', 'allow_comments', 'category', 'created_at')
    search_fields = ('title', 'description', 'user__username')
    ordering = ('-created_at',)
    inlines = [CommentInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'title', 'description', 'category')
        }),
        ('Image Options', {
            'fields': ('image_upload', 'image_url'),
            'description': 'Either upload an image or provide a URL. If both are provided, the upload will be used.'
        }),
        ('Settings', {
            'fields': ('hide', 'allow_comments')
        }),
    )
    
    def author(self, obj):
        return obj.user.username
    author.short_description = 'Author'
    
    def has_image(self, obj):
        if obj.image_upload or obj.image_url:
            return format_html('<span style="color: green;">✓</span>')
        return format_html('<span style="color: red;">✗</span>')
    has_image.short_description = 'Has Image'
    
    def hidden_status(self, obj):
        if obj.hide:
            return format_html('<span style="color: red;">Hidden</span>')
        return format_html('<span style="color: green;">Visible</span>')
    hidden_status.short_description = 'Status'
    
    def comments_enabled(self, obj):
        if obj.allow_comments:
            return format_html('<span style="color: green;">Enabled</span>')
        return format_html('<span style="color: red;">Disabled</span>')
    comments_enabled.short_description = 'Comments'


class CommentAdmin(admin.ModelAdmin):
    list_display = ('comment_preview', 'author', 'post_title', 'hidden_status', 'added_at')
    list_filter = ('hide', 'added_at', 'post__category')
    search_fields = ('text', 'user__username', 'post__title')
    ordering = ('-added_at',)
    inlines = [ReplyInline]
    
    readonly_fields = ('added_at',)
    
    def comment_preview(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    comment_preview.short_description = 'Comment Preview'
    
    def author(self, obj):
        return obj.user.username
    author.short_description = 'Author'
    
    def post_title(self, obj):
        return obj.post.title
    post_title.short_description = 'On Post'
    
    def hidden_status(self, obj):
        if obj.hide:
            return format_html('<span style="color: red;">Hidden</span>')
        return format_html('<span style="color: green;">Visible</span>')
    hidden_status.short_description = 'Status'


class ReplyAdmin(admin.ModelAdmin):
    list_display = ('reply_preview', 'author', 'parent_comment', 'parent_post', 'hidden_status', 'added_at')
    list_filter = ('hide', 'added_at', 'comment__post__category')
    search_fields = ('text', 'user__username', 'comment__text', 'comment__post__title')
    ordering = ('-added_at',)
    
    readonly_fields = ('added_at',)
    
    def reply_preview(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    reply_preview.short_description = 'Reply Preview'
    
    def author(self, obj):
        return obj.user.username
    author.short_description = 'Author'
    
    def parent_comment(self, obj):
        comment_preview = obj.comment.text[:30] + '...' if len(obj.comment.text) > 30 else obj.comment.text
        return f"by {obj.comment.user.username}: {comment_preview}"
    parent_comment.short_description = 'Replying to Comment'
    
    def parent_post(self, obj):
        return obj.comment.post.title
    parent_post.short_description = 'On Post'
    
    def hidden_status(self, obj):
        if obj.hide:
            return format_html('<span style="color: red;">Hidden</span>')
        return format_html('<span style="color: green;">Visible</span>')
    hidden_status.short_description = 'Status'


class SavedAdmin(admin.ModelAdmin):
    list_display = ('user_name', 'post_title', 'post_author', 'saved_at')
    list_filter = ('saved_at', 'post__category')
    search_fields = ('user__username', 'post__title', 'post__user__username')
    ordering = ('-saved_at',)
    
    readonly_fields = ('saved_at',)
    
    def user_name(self, obj):
        return obj.user.username
    user_name.short_description = 'Saved by'
    
    def post_title(self, obj):
        return obj.post.title
    post_title.short_description = 'Post Title'
    
    def post_author(self, obj):
        return obj.post.user.username
    post_author.short_description = 'Post Author'


# Register the models with their admin classes
admin.site.register(Category, CategoryAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Reply, ReplyAdmin)
admin.site.register(Saved, SavedAdmin)