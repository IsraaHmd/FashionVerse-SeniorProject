from django.http import JsonResponse,HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.core.paginator import Paginator
from .models import *
from django.contrib import messages
from django.core.exceptions import ValidationError
import os
from django.db.models import Q, Exists, OuterRef
#--------------------------------------------------------------------
# Check login
def check_login(request):
    #Check if the user is authenticated
    if not request.user.is_authenticated:
        #Check if the request is ajax
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            #If it is an ajax request, then return a response that shows the authentication status 
            """
            Why do that:
            Instead of sending back the expected data (like product details or whatever your AJAX call is supposed to get), the server detects that the user is not authenticated
            The server sends the response below instead of the expected one
            In the frontend(js) we should check which response is returned and handle it
            """
            return JsonResponse({
                'authenticated': False,
                'login_url': reverse('users:login'),
                'shop_url': reverse('shop:index')
            })
        #For non-ajax requests that are done by unauthenticated users just return false
        return False
    return True
#------------------------------------------------------------------------------------------------
# Create Post
def create_post(request):
    # Check if user is logged in
    auth_check = check_login(request)
    if auth_check is not True:
        if isinstance(auth_check, JsonResponse):
            return auth_check
        return render(request, 'community/login_required_modal.html', {
            'login_url': reverse('users:login'),
            'shop_url': reverse('shop:index')
        })
    
    # Get the base context for header/base template
    context = get_base_context(request)
    
    # Add all categories for dropdown
    categories = Category.objects.all().order_by('name')
    context['categories'] = categories
    
    # Handle AJAX request for creating a new category
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' and request.method == 'POST':
        if 'create_category' in request.POST:
            return create_category_ajax(request)
        
    # Handle form submission
    if request.method == 'POST' and 'create_category' not in request.POST:
        try:
            # Get form data
            data = request.POST 
            title = data.get('title', '').strip()
            description = data.get('description', '').strip() # if description exists in data then get it otherwise ''
            category_id = data.get('category_id')
            allow_comments = 'allow_comments' in data
            
            # Validate required fields
            errors = {}
            if not title:
                errors['title'] = "Title is required"
            
            category = None
            if category_id:
                try:
                    category = Category.objects.get(id=category_id)
                except Category.DoesNotExist:
                    errors['category'] = "Selected category does not exist, create it!"

            # Handle image upload or URL
            image_upload = request.FILES.get('image_upload')
            image_url = data.get('image_url', '').strip()
            
            if not image_upload and not image_url:
                errors['image'] = "Either an image file or URL is required"
            
            # If there are validation errors, return them as JSON
            if errors:
                # Save form data to repopulate the form
                context['form_data'] = {
                    'title': title,
                    'description': description,
                    'category_id': category_id,
                    'allow_comments': allow_comments,
                    'image_url': image_url,
                    'has_image_upload': bool(image_upload)  # Add flag for frontend
                }
                context['errors'] = errors
                return render(request, 'community/create_post.html', context)
            
            # Create the post
            post = Post(
                user=request.user,
                title=title,
                description=description,
                category=category,
                allow_comments=allow_comments
            )
            
            # Set image (upload takes precedence over URL)
            if image_upload:
                post.image_upload = image_upload
                post.image_url = None
            else:
                post.image_url = image_url
                post.image_upload = None
            
            # Save the post
            post.clean()  # Run model validation
            post.save()
            
            # Redirect to the new post or return success JSON response
            #messages.success(request, "Post created successfully!")
            return redirect('community:post_detail', post_id=post.id)
                
        except ValidationError as ve:
            # Handle model validation errors
            error_dict = {}
            if hasattr(ve, 'message_dict'):
                error_dict = ve.message_dict
            else:
                error_dict['general'] = list(ve.messages)
            # Add errors to context to display in form
            context['errors'] = error_dict
            # Save form data to repopulate the form
            context['form_data'] = {
                'title': data.get('title', ''),
                'description': data.get('description', ''),
                'category_id': data.get('category_id') if data.get('category_id') else None,
                'allow_comments': 'allow_comments' in data,
                'image_url': data.get('image_url', ''),
                'has_image_upload': bool(image_upload)  # Add flag for frontend
            }
        except Exception as e:
            # Handle other exceptions
            messages.error(request, f"An error occurred: {str(e)}")
            
            # Save form data to repopulate the form
            context['form_data'] = {
                'title': data.get('title', ''),
                'description': data.get('description', ''),
                'category_id': data.get('category_id') if data.get('category_id') else None,
                'allow_comments': 'allow_comments' in data,
                'image_url': data.get('image_url', ''),
                'has_image_upload': bool(image_upload)  # Add flag for frontend
            }
    
    return render(request, 'community/create_post.html', context)

#Edit Post:
def edit_post(request, post_id):
    """
    View for editing an existing post
    """
    # Check if user is logged in
    auth_check = check_login(request)
    if auth_check is not True:
        if isinstance(auth_check, JsonResponse):
            return auth_check
        return redirect('users:login')
    
    # Get the post or return 404 if not found
    post = get_object_or_404(Post, id=post_id)
    
    # Check if the user owns this post or is a superuser
    if post.user != request.user and not request.user.is_superuser:
        return HttpResponseForbidden("You don't have permission to edit this post.")
    
    # Get the base context for header/base template
    context = get_base_context(request)
    
    # Add all categories for dropdown
    categories = Category.objects.all().order_by('name')
    context['categories'] = categories
    context['post'] = post
    
    # Handle AJAX request for creating a new category
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' and request.method == 'POST':
        if 'create_category' in request.POST:
            return create_category_ajax(request)
    
    # Handle form submission
    if request.method == 'POST' and 'create_category' not in request.POST:
        try:
            # Get form data
            data = request.POST 
            title = data.get('title', '').strip()
            description = data.get('description', '').strip()
            category_id = data.get('category_id')
            allow_comments = 'allow_comments' in data
            
            # Validate required fields
            errors = {}
            if not title:
                errors['title'] = "Title is required"
            
            category = None
            if category_id:
                try:
                    category = Category.objects.get(id=category_id)
                except Category.DoesNotExist:
                    errors['category'] = "Selected category does not exist, create it!"
            
            # Handle image upload or URL
            image_upload = request.FILES.get('image_upload')
            image_url = data.get('image_url', '').strip()
            
            # Only validate image if both current image options are empty AND no new image is provided
            if not post.image_upload and not post.image_url and not image_upload and not image_url:
                errors['image'] = "Either an image file or URL is required"
            
            # If there are validation errors, return them with the form
            if errors:
                # Save form data to repopulate the form
                context['form_data'] = {
                    'title': title,
                    'description': description,
                    'category_id': category_id,
                    'allow_comments': allow_comments,
                    'image_url': image_url,
                    'has_image_upload': bool(image_upload)
                }
                context['errors'] = errors
                return render(request, 'community/edit_post.html', context)
            
            # Update the post with new values
            post.title = title
            post.description = description
            post.category = category
            post.allow_comments = allow_comments
            
            # Update image (upload takes precedence over URL)
            if image_upload:
                # If switching from URL to upload or replacing an existing upload
                #if post.image_upload:
                    # Delete the old image file since there is a new upload
                    #delete_old_image(post)
                
                # If there's a new upload, use it and clear URL
                post.image_upload = image_upload
                post.image_url = None
            elif image_url:
                # If switching from upload to URL
                #if post.image_upload:
                    # Delete the old image file
                    #delete_old_image(post)
                
                # If there's a new URL but no new upload, use the URL and clear upload
                post.image_url = image_url
                post.image_upload = None

            # If neither image_upload nor image_url is provided, keep the existing values
            # Save the post
            post.clean()  # Run model validation
            post.save()
            
            # Redirect to the updated post
            #messages.success(request, "Post updated successfully!")
            return redirect('community:post_detail', post_id=post.id)
                
        except ValidationError as ve:
            # Handle model validation errors
            error_dict = {}
            if hasattr(ve, 'message_dict'):
                error_dict = ve.message_dict
            else:
                error_dict['general'] = list(ve.messages)
            # Add errors to context to display in form
            context['errors'] = error_dict
            # Save form data to repopulate the form
            context['form_data'] = {
                'title': data.get('title', ''),
                'description': data.get('description', ''),
                'category_id': data.get('category_id') if data.get('category_id') else None,
                'allow_comments': 'allow_comments' in data,
                'image_url': data.get('image_url', ''),
                'has_image_upload': bool(image_upload)  # Add flag for frontend
            }
        except Exception as e:
            # Handle other exceptions
            messages.error(request, f"An error occurred: {str(e)}")
            
            # Save form data to repopulate the form
            context['form_data'] = {
                'title': data.get('title', ''),
                'description': data.get('description', ''),
                'category_id': data.get('category_id') if data.get('category_id') else None,
                'allow_comments': 'allow_comments' in data,
                'image_url': data.get('image_url', ''),
                'has_image_upload': bool(image_upload)  # Add flag for frontend
            }
    
    return render(request, 'community/edit_post.html', context)

#Delete the old image if the user 
def delete_old_image(post):
    """
    Delete the old image file from storage if it exists
    """
    if post.image_upload and hasattr(post.image_upload, 'path'):
        try:
            if os.path.isfile(post.image_upload.path):
                os.remove(post.image_upload.path)
                return True
        except Exception as e:
            # Log the error but don't raise it to avoid interfering with the main flow
            print(f"Error deleting old image: {e}")
    return False

def delete_post(request, post_id):
    """
    View for "deleting" a post (setting hide=True)
    """
    # Check if user is logged in
    auth_check = check_login(request)
    if auth_check is not True:
        if isinstance(auth_check, JsonResponse):
            return auth_check
        return redirect('users:login')
    
    # Get the post
    post = get_object_or_404(Post, id=post_id)
    
    # Check if the user owns this post or is a superuser
    if post.user != request.user and not request.user.is_superuser:
        return HttpResponseForbidden("You don't have permission to delete this post.")
    
    # Handle the form submission (from the modal)
    if request.method == 'POST':
        # Mark post as hidden instead of deleting
        post.hide = True
        post.save()
        
        # Redirect to profile page
        return redirect('community:profile')
    
    # If not POST, redirect back to the referring page
    return redirect(request.META.get('HTTP_REFERER', 'community:homepage'))

def create_category_ajax(request):
    """
    Handle AJAX request for creating a new category
    Returns JsonResponse with the created/existing category details
    """
    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)
    
    if 'create_category' not in request.POST:
        return JsonResponse({'success': False, 'error': 'Invalid category creation request'}, status=400)
        
    try:
        category_name = request.POST.get('category_name', '').strip()
        
        if not category_name:
            return JsonResponse({'success': False, 'error': 'Category name cannot be empty'}, status=400)
        
        # Check if category already exists (case insensitive)
        existing_category = Category.objects.filter(name__iexact=category_name).first()
        if existing_category:
            return JsonResponse({
                'success': True, 
                'id': existing_category.id, 
                'name': existing_category.name
            })
        
        # Create new category
        category = Category.objects.create(name=category_name)
        return JsonResponse({
            'success': True, 
            'id': category.id, 
            'name': category.name
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

# -------------------------------------------------------------------------------------------------
#Saved
def save_post(request, post_id):
    """
    View for saving or unsaving a post
    """
    # Check if user is logged in
    auth_check = check_login(request)
    if auth_check is not True:
        if isinstance(auth_check, JsonResponse):
            return auth_check
        return redirect('users:login')
    
    # Get the post
    post = get_object_or_404(Post, id=post_id)
    
    # Check if the post is already saved
    saved_entry = Saved.objects.filter(user=request.user, post=post).first()
    
    if request.method == 'POST':
        # Toggle saved status
        if saved_entry:
            # If already saved, remove it (unsave)
            saved_entry.delete()
            is_saved = False
        else:
            # If not saved, save it
            Saved.objects.create(user=request.user, post=post)
            is_saved = True
        
        # Return JSON response for AJAX requests
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'is_saved': is_saved,
                'message': 'Post saved successfully!' if is_saved else 'Post removed from saved items.'
            })
        
        # For non-AJAX requests, redirect back to the referring page
        return redirect(request.META.get('HTTP_REFERER', 'community:homepage'))
    
    # If not POST, redirect back to the referring page
    return redirect(request.META.get('HTTP_REFERER', 'community:homepage'))

#--------------------------------------------------------------------------------------------------
#Comments and Replies: 
def add_comment(request, post_id):
    """
    View for adding a comment to a post
    """
    # Check if user is logged in
    auth_check = check_login(request)
    if auth_check is not True:
        if isinstance(auth_check, JsonResponse):
            return auth_check
        return redirect('users:login')
    
    # Get the post
    post = get_object_or_404(Post, id=post_id)
    
    # Check if comments are allowed on this post
    if not post.allow_comments:
        messages.error(request, "Comments are not allowed on this post.")
        return redirect('community:post_detail', post_id=post_id)
    
    if request.method == 'POST':
        # Get the comment text from the form
        comment_text = request.POST.get('comment_text', '').strip()
        
        if not comment_text:
            messages.error(request, "Comment cannot be empty.")
            return redirect('community:post_detail', post_id=post_id)
        
        try:
            # Create the comment
            comment = Comment(
                user=request.user,
                post=post,
                text=comment_text
            )
            comment.clean()  # Run validation
            comment.save()
            
            #messages.success(request, "Comment added successfully.")
        except ValidationError as ve:
            if hasattr(ve, 'message_dict'):
                for field, errors in ve.message_dict.items():
                    for error in errors:
                        messages.error(request, error)
            else:
                messages.error(request, ve)
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
    
    # Redirect back to the post detail page
    return redirect('community:post_detail', post_id=post_id)

def delete_comment(request, comment_id):
    """
    View for "deleting" (hiding) a comment
    """
    # Check if user is logged in
    auth_check = check_login(request)
    if auth_check is not True:
        if isinstance(auth_check, JsonResponse):
            return auth_check
        return redirect('users:login')
    
    # Get the comment
    comment = get_object_or_404(Comment, id=comment_id)
    
    # Check if the user owns this comment
    if comment.user != request.user:
        return HttpResponseForbidden("You don't have permission to delete this comment.")
    
    # Handle the confirmation request
    if request.method == 'POST':
        # Mark comment as hidden instead of deleting
        comment.hide = True
        comment.save()
        
        #messages.success(request, "Comment deleted successfully.")
        return redirect('community:post_detail', post_id=comment.post.id)
    
    # For GET requests, just redirect back to the post detail page
    # The confirmation is handled by JavaScript
    return redirect('community:post_detail', post_id=comment.post.id)

def add_reply(request, comment_id):
    """
    View for adding a reply to a comment
    """
    # Check if user is logged in
    auth_check = check_login(request)
    if auth_check is not True:
        if isinstance(auth_check, JsonResponse):
            return auth_check
        return redirect('users:login')
    
    # Get the comment
    comment = get_object_or_404(Comment, id=comment_id)
    
    # Check if comments are allowed on the parent post
    if not comment.post.allow_comments:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': "Comments and replies are not allowed on this post."})
        messages.error(request, "Comments and replies are not allowed on this post.")
        return redirect('community:post_detail', post_id=comment.post.id)
    
    if request.method == 'POST':
        # Get the reply text from the form
        reply_text = request.POST.get('reply_text', '').strip()
        
        if not reply_text:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': "Reply cannot be empty."})
            messages.error(request, "Reply cannot be empty.")
            return redirect('community:post_detail', post_id=comment.post.id)
        
        try:
            # Create the reply
            reply = Reply(
                user=request.user,
                comment=comment,
                text=reply_text
            )
            reply.clean()  # Run validation
            reply.save()
            
            # If this is an AJAX request, return JSON response
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                # Prepare reply data for JSON response
                reply_data = {
                    'id': reply.id,
                    'text': reply.text,
                    'user': {
                        'username': reply.user.username,
                        'initial': reply.user.username[0].upper(),
                        'profile_image': reply.user.profile_image_upload.url if hasattr(reply.user, 'profile_image_upload') and reply.user.profile_image_upload else None,
                    },
                    'added_at': reply.added_at.strftime("%B %d, %Y, %I:%M %p"),
                    'is_owner': reply.user == request.user
                }
                return JsonResponse({'success': True, 'reply': reply_data})
            
            #messages.success(request, "Reply added successfully.")
        except ValidationError as ve:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                if hasattr(ve, 'message_dict'):
                    return JsonResponse({'success': False, 'error': ve.message_dict})
                else:
                    return JsonResponse({'success': False, 'error': str(ve)})
            
            if hasattr(ve, 'message_dict'):
                for field, errors in ve.message_dict.items():
                    for error in errors:
                        messages.error(request, error)
            else:
                messages.error(request, ve)
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': str(e)})
            
            messages.error(request, f"An error occurred: {str(e)}")
    
    # For non-AJAX requests, redirect back to the post detail page
    return redirect('community:post_detail', post_id=comment.post.id)

def delete_reply(request, reply_id):
    """
    View for "deleting" (hiding) a reply
    """
    # Check if user is logged in
    auth_check = check_login(request)
    if auth_check is not True:
        if isinstance(auth_check, JsonResponse):
            return auth_check
        return redirect('users:login')
    
    # Get the reply
    reply = get_object_or_404(Reply, id=reply_id)
    
    # Check if the user owns this reply
    if reply.user != request.user:
        return HttpResponseForbidden("You don't have permission to delete this reply.")
    
    # Handle the confirmation request
    if request.method == 'POST':
        # Mark reply as hidden instead of deleting
        reply.hide = True
        reply.save()
        
        #messages.success(request, "Reply deleted successfully.")
        return redirect('community:post_detail', post_id=reply.comment.post.id)
    
    # For GET requests, just redirect back to the post detail page
    # The confirmation is handled by JavaScript
    return redirect('community:post_detail', post_id=reply.comment.post.id)

#------------------------------------------------------------------------------------------
#Post detail display
def post_detail(request, post_id):
    """
    View for displaying a specific post and its comments
    """
    # Check if user is logged in
    auth_check = check_login(request)
    if auth_check is not True:
        if isinstance(auth_check, JsonResponse):
            return auth_check
        return render(request, 'community/login_required_modal.html', {
            'login_url': reverse('users:login'),
            'shop_url': reverse('shop:index')
        })
    
    # Get the post or return 404 if not found
    post = get_object_or_404(Post, id=post_id, hide=False)
    
    # Get comments that aren't hidden
    comments = Comment.objects.filter(post=post, hide=False).select_related('user')
    
    # Get replies for each comment
    for comment in comments:
        comment.all_replies = Reply.objects.filter(comment=comment, hide=False).select_related('user')
    
    # Check if the user has saved this post
    is_saved = False
    if request.user.is_authenticated:
        is_saved = Saved.objects.filter(user=request.user, post=post).exists()
    
    # Get base context for header/base template
    context = get_base_context(request)
    
    # Add post-specific context
    context.update({
        'post': post,
        'comments': comments,
        'is_saved': is_saved,
        'current_user': request.user,
    })
    
    return render(request, 'community/view_post.html', context)

#------------------------------------------------------------------------------------------
# Profile
def profile(request):
    """
    View for the user profile page showing user information and posts
    """
    # Check if user is logged in
    auth_check = check_login(request)
    if auth_check is not True:
        if isinstance(auth_check, JsonResponse):
            return auth_check
        return render(request, 'community/login_required_modal.html', {
            'login_url': reverse('users:login'),
            'shop_url': reverse('shop:index')
        })
    
    # Get the base context for header/base template
    context = get_base_context(request)
    
    # Check for active tab in query parameters
    active_tab = request.GET.get('tab', 'created')
    
    # Only fetch the data needed for the active tab
    if active_tab == 'saved':
        # Get the user's saved posts
        posts = Post.objects.filter(
            saved_by__user=request.user,
            hide=False
        ).select_related('category', 'user')
        for post in posts:
            post.is_saved = True
        context['saved_posts'] = posts
    else:  # default to 'created' tab
        # Get the user's created posts
        posts = Post.objects.filter(
            user=request.user,
            hide=False
        ).select_related('category')
        # Annotate with saved status for created posts
        if request.user.is_authenticated:
            saved_subquery = Saved.objects.filter(
                user=request.user,
                post_id=OuterRef('pk')
            )
            posts = posts.annotate(
                is_saved=Exists(saved_subquery)
            )
        context['user_posts'] = posts
        active_tab = 'created'  # Ensure we're using the correct tab name
    
    # Add user profile data to context
    context.update({
        'active_tab': active_tab,
        'profile': {
            'username': request.user.username,
            'email': request.user.email,
            'initial': request.user.username[0].upper() if request.user.username else 'U',
            'profile_image': request.user.profile_image_upload.url if hasattr(request.user, 'profile_image_upload') and request.user.profile_image_upload else None,
        }
    })
    
    return render(request, 'community/profile.html', context)

def profile_saved(request):
    """
    Redirect to profile view with saved tab active
    """
    return redirect(reverse('community:profile') + '?tab=saved')

#------------------------------------------------------------------------------------------
def search(request):
    """
    View for the search results page
    """
    # Check if user is logged in
    auth_check = check_login(request)
    if auth_check is not True:
        if isinstance(auth_check, JsonResponse):
            return auth_check
        return render(request, 'community/login_required_modal.html', {
            'login_url': reverse('users:login'),
            'shop_url': reverse('shop:index')
        })
    print('success')
    # Get the search query from GET parameters
    query = request.GET.get('q', '').strip()
    
    # Get base context for header/base template
    context = get_base_context(request)
    
    # Start with all non-hidden posts
    posts = Post.objects.filter(hide=False).select_related('category', 'user')
    
    # If there's a search query, filter the posts
    if query:
        # Search in title, category name, and description
        # Using icontains for case-insensitive partial matching
        posts = posts.filter(
            models.Q(title__icontains=query) |
            models.Q(category__name__icontains=query) |
            models.Q(description__icontains=query)|
            models.Q(user__username__icontains=query)
        ).distinct()
    
    # Annotate with saved status for the user if authenticated
    if request.user.is_authenticated:
        saved_subquery = Saved.objects.filter(
            user=request.user,
            post_id=OuterRef('pk')
        )
        
        posts = posts.annotate(
            is_saved=Exists(saved_subquery)
        )
    
    # Pagination to avoid loading too many posts at once
    paginator = Paginator(posts, 50)  # Show 50 posts per page
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Add search-specific context
    context.update({
        'pins': page_obj,
        'search_query': query,
        'search_results_count': paginator.count,
    })
    
    return render(request, 'community/search_results.html', context)


#-------------------------------------------------------------------------------------

#Get the context to display in base.html:
def get_base_context(request):
    """Get common context data needed for header/base template"""
    context = {}
    
    # Add user data for profile image/display
    if request.user.is_authenticated:
        context['user_profile'] = {
            'username': request.user.username,
            'email': request.user.email,
            'initial': request.user.username[0].upper() if request.user.username else 'U',
            # Add profile image if it exists
            'profile_image': request.user.profile_image_upload.url if request.user.profile_image_upload else None,
        }
    
    return context

from django.db.models import Exists, OuterRef

def homepage(request):
    # Check if user is logged in
    auth_check = check_login(request)
    if auth_check is not True:
        if isinstance(auth_check, JsonResponse):
            return auth_check
        return render(request, 'community/login_required_modal.html', {
            'login_url': reverse('users:login'),
            'shop_url': reverse('shop:index')
        })

    # User is authenticated, get base context for header/base template
    context = get_base_context(request)
    
    # Get all posts that are not hidden and select related categories
    posts = Post.objects.filter(hide=False).select_related('category')
    
    # Annotate with saved status for the user
    if request.user.is_authenticated:
        saved_subquery = Saved.objects.filter(
            user=request.user,
            post_id=OuterRef('pk')
        )
        
        posts = posts.annotate(
            is_saved=Exists(saved_subquery)
        )
    
    # Pagination to avoid loading too many posts at once
    paginator = Paginator(posts, 50)  # Show 50 posts per page
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Add page-specific context
    context.update({
        'pins': page_obj,  
    })
    
    return render(request, 'community/homepage.html', context)

"""
Note: isinstance(): 
isinstance(auth_check, JsonResponse) check ensures that:

Only AJAX requests get a JSON error

Other requests can be handled differently
“If check_login did not return True, then it must have returned either False or a JsonResponse.
Now let's check: if it returned a JsonResponse, just return that (because it's an AJAX request and expects a JSON error).”

"""