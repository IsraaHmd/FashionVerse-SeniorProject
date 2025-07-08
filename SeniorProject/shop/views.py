from django.http import HttpResponse,JsonResponse
from django.shortcuts import redirect, render #, get_object_or_404
from .models import *
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
import traceback
import logging
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.urls import reverse

def index(request):
    # Fetch the 4 most recent products
    recent_products = Product.objects.filter(hide=False).order_by('-created_at')[:4]
    
    # For each product, get its first visible color variant
    recent_product_colors = []
    for product in recent_products:
        # Get the first visible color variant for this product
        product_color = ProductColor.objects.filter(
            product=product,
            hide=False
        ).first()
        
        if product_color:
            # If user is authenticated, check if it's in their wishlist
            if request.user.is_authenticated:
                is_in_wishlist = WishlistItem.objects.filter(
                    user=request.user,
                    product_color=product_color
                ).exists()
                product_color.in_wishlist = is_in_wishlist
            else:
                product_color.in_wishlist = False
                
            recent_product_colors.append(product_color)
    
    return render(request, 'shop/index.html', {'recent_product_colors': recent_product_colors})

def about(request):
    return render(request, 'shop/aboutus.html')

def shop(request):
    # Fetch all product colors and join the product data using select_related, note that products variable is a queryset of ProductColor objects, not their parent Product objects
    products_colors = ProductColor.objects.select_related('product').filter(
        hide=False,  # Only show visible product colors
        product__hide=False  # Only show colors of visible products
    ).order_by('-product__created_at').all()
    # Check for order success flag
    order_success = request.session.pop('order_success', False)
    # If user is authenticated, annotate wishlist status directly in the query
    # .annotate() adds an extra field ('in_wishlist') to each item in the queryset(One sql query is performaed), 
    # which is True or False depending on whether the product color is in the wishlist for the specific user (request.user).
    
    if request.user.is_authenticated:
        from django.db.models import Exists, OuterRef
        
        # Subquery to check if this product color exists in user's wishlist
        wishlist_subquery = WishlistItem.objects.filter(
            user=request.user,
            product_color_id=OuterRef('pk')
        )
        
        # Annotate each product with wishlist status in a single database query
        products_colors = products_colors.annotate(
            in_wishlist=Exists(wishlist_subquery) 
        )
    # Pass product_colors to the template
    return render(request, 'shop/shop.html', {'products_colors': products_colors, 'order_success': order_success})

def shop_item(request, item_id):
    #item_id is the id of the product color
    product_color = None
    not_found_message = ''

    try:
        #we are using query below then getting the product_color later since we can't use .annotate() on a single object, as it's meant for querysets.
        #notice that we are using filter not get because: .get() returns a model instance, not a queryset. 
        query = ProductColor.objects.prefetch_related('variants').filter(
            id=item_id,
            hide=False, # Only show if this color isn't hidden
            product__hide=False # Only show if the product isn't hidden
        )
        
        # Add wishlist information if user is authenticated
        if request.user.is_authenticated:
            from django.db.models import Exists, OuterRef
            wishlist_subquery = WishlistItem.objects.filter(
                user=request.user,
                product_color_id=OuterRef('pk')
            )
            
            query = query.annotate(in_wishlist=Exists(wishlist_subquery))
        
        product_color = query.get()
    except ProductColor.DoesNotExist:
        not_found_message = 'Product not found'
        context = {'not_found_message': not_found_message}
        return render(request, 'shop/shopItem.html', context)

    #Get the product(ProductColor has a fk ref to it )
    product = product_color.product
    #Get the product variant(sizes and its quanitity of this product color)
    product_variants = product_color.variants.filter(hide=False).all()
    # Get all the product color objects related to this product
    all_product_colors = product.color_variants.filter(hide=False).all()

    context = {
        'product': product,
        'product_color': product_color,
        'variants': product_variants,
        'not_found_message': '',
        'all_product_colors':all_product_colors
    }
    
    return render(request, 'shop/shopItem.html', context)

"""
was for prod colors ajax
# Upon selecting the color in the product, to fetch the product: 
from django.http import JsonResponse

def get_product_variants(request, product_color_id):
    try:
        product_color = ProductColor.objects.get(id=product_color_id)
        product_image = product_color.get_image()  # Get the image URL for the selected color
        variants = product_color.variants.all().values('size__name', 'quantity')  # Fetch size and quantity
        total_color_stock = product_color.total_product_color_stock
        # Prepare the response data
        variant_data = list(variants)
        
        return JsonResponse({
            'product_image': product_image,
            'variants': variant_data,
            'total_color_stock': total_color_stock,
        })
    except ProductColor.DoesNotExist:
        return JsonResponse({'not_found_message': 'Product not found'}, status=404)
"""        

""" The below function was supposed to be used for "view cart" functionality but since the cart is as if a part of everypage, not a page onits own
# cart
def cart(request):
    # Make sure you handle unauthenticated users properly
    if not request.user.is_authenticated:
        return render(request, 'shop/cart.html', {
            'cart_items': [],
            'total': 0,
            'cart_total_quantity': 0
        })
    # Select related fields to avoid multiple database queries, below as if we are joining the cart items table with the prod, proc color, prod variant, color and sizes table where the item belogs to this user and not hidden
    cart_items = CartItem.objects.filter(
        user=request.user,
        product_variant__hide=False,
        product_variant__product_color__hide=False,
        product_variant__product_color__product__hide=False
    ).select_related(
        'product_variant__product_color__product', # Get the Product related to the ProductColor related to the ProductVariant in one go. so now we can acess the product variant, its product color, and its product
        'product_variant__product_color__color', # Get the Color of the ProductColor.
        'product_variant__size' # Get the Size of the variant directly.
    )
    print(f"Cart items found: {cart_items.count()}")
    if cart_items.count() > 0:
        print(f"First item: {cart_items[0].product_variant.product_color.product.title}")
    # Calculate total
    total = sum(item.subtotal() for item in cart_items)
    
    # Get available sizes for each product color
    for item in cart_items:
        product_color = item.product_variant.product_color
        item.available_sizes = ProductVariant.objects.filter(
            product_color=product_color,
            hide=False, 
            quantity__gt=0  # get the sizes that have quanitity>0
        ).select_related('size') #get the size of the product variant of this prod color, that is not hidden and has stock
    
    # after this loop, as if each item in cart_items has the attribute available sizes which is not a model attribute (not stored in database), but could be accessed in template by for item in cart_items: .. item.available_sizes
    # note that item.available_sizes is a queryset (as if an array)

    # total quantity, including the quantity of each item
    cart_total_quantity = sum(item.quantity for item in cart_items)

    return render(request, 'shop/cart.html', {
        'cart_items': cart_items,
        'total': total,
        'cart_total_quantity': cart_total_quantity
    })
"""
#Add to cart
def add_to_cart(request):
    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, "Please login to add to cart.")
            product_color_id = request.POST.get('product_color_id')
            if product_color_id:
                return redirect('shop:shop_item', item_id=product_color_id)
            else:
                return redirect('shop:shop')
            
        variant_id = request.POST.get('variant_id')
        product_color_id = request.POST.get('product_color_id') 

        # Check if variant_id is empty or None
        if not variant_id:
            # User hasn't selected a size
            messages.error(request, "Please choose a size before adding to cart.")
            return redirect('shop:shop_item', item_id=product_color_id)
            # was return shop_item(request, item_id=product_color_id, message="Please choose a size before adding to cart.")
        
        try:
            # Try to get the product variant
            variant = ProductVariant.objects.select_related(
                'product_color__product', 
                'product_color__color', 
                'size'
            ).get(
                id=variant_id,
                hide=False,
                product_color__hide=False,
                product_color__product__hide=False
            )
            
            # Check if any stock is available
            if variant.quantity <= 0:
                # Render the product detail template with out of stock message
                messages.error(request, "This product is out of stock.")
                return redirect('shop:shop_item', item_id=product_color_id)
            
            # Get or create cart item
            cart_item, created = CartItem.objects.get_or_create(
                user=request.user,
                product_variant=variant,
                defaults={'quantity': 1}
            )
            
            # If already exists, update quantity
            if not created:
                new_quantity = cart_item.quantity + 1
                if new_quantity > variant.quantity:
                    # Render the product detail template with max quantity message
                    messages.error(request, "Maximum quantity of this product is already in your cart.")
                    return redirect('shop:shop_item', item_id=product_color_id)
                
                cart_item.quantity = new_quantity
                cart_item.save()
            
            # Redirect to view cart on success
            print("Success")
            #return to previous page(in this case it is probably shopItem) with cart open
            next_url = request.META.get('HTTP_REFERER', '')
            if '?' in next_url:
                return redirect(f"{next_url}&open_cart=true")
            else:
                return redirect(f"{next_url}?open_cart=true")

            
        except ProductVariant.DoesNotExist:
            messages.error(request, "There was an issue with the selected product. Please try again.")
            return redirect('shop:shop_item', item_id=product_color_id)

        except Exception as e:
            print(e)
            messages.error(request, "An unexpected error occurred. Please try again later.")
            return redirect('shop:shop_item', item_id=product_color_id)

    # If GET request or any other issues, redirect to shop
    return redirect('shop:shop')

def remove_from_cart(request, item_id):
    if request.user.is_authenticated:
        try:
            # Find and delete the cart item
            cart_item = CartItem.objects.get(id=item_id, user=request.user)
            cart_item.delete()
            # You could add a success message here if you're using Django messages framework
        except CartItem.DoesNotExist:
            # You could add an error message here
            return redirect('shop:shop')
    
    # Redirect back to the referring page with a parameter to reopen the cart, so the site is like 127.0.0.1/shop/?open_cart=true
    next_url = request.META.get('HTTP_REFERER', '')
    if '?' in next_url:
        return redirect(f"{next_url}&open_cart=true")
    else:
        return redirect(f"{next_url}?open_cart=true")
    #open_cart will be used in cart.js to reopen the cart

# Update cart: Update size:
def update_cart_size(request, item_id):
    if request.user.is_authenticated:
        try:
            # Get the cart item
            cart_item = CartItem.objects.get(id=item_id, user=request.user)
            
            # Get the new variant ID from request
            new_variant_id = request.POST.get('variant_id')
            if not new_variant_id:
                return redirect('shop:shop')
                
            # Get the new variant
            new_variant = ProductVariant.objects.get(
                id=new_variant_id, 
                hide=False,
                quantity__gt=0
            )
            
            # Check if there's already another cart item with this variant
            existing_item = CartItem.objects.filter(
                user=request.user,
                product_variant=new_variant
            ).first()
            
            if existing_item and existing_item.id != cart_item.id:
                # Combine quantities (respecting stock limits)
                combined_quantity = existing_item.quantity + cart_item.quantity
                if combined_quantity > new_variant.quantity:
                    combined_quantity = new_variant.quantity
                    # Prepare message about limiting quantity
                    message = f"Quantity adjusted to maximum available stock of the size {new_variant.size}"
                    request.session['cart_message'] = message
                
                existing_item.quantity = combined_quantity
                existing_item.save()
                cart_item.delete()
            else:
                # Update the variant and adjust quantity if needed
                if cart_item.quantity > new_variant.quantity:
                    cart_item.quantity = new_variant.quantity
                    # Here we'll prepare a message - moved to this location
                    message = f"Quantity adjusted to maximum available stock of the size {new_variant.size}"
                    # Store message in session to display after redirect
                    request.session['cart_message'] = message
                
                cart_item.product_variant = new_variant
                cart_item.save()
                
        except (CartItem.DoesNotExist, ProductVariant.DoesNotExist):
            pass
            
    # Redirect back to the referring page with cart open
    next_url = request.META.get('HTTP_REFERER', '')
    if '?' in next_url:
        return redirect(f"{next_url}&open_cart=true")
    else:
        return redirect(f"{next_url}?open_cart=true")
    
# More simplified view for debugging


logger = logging.getLogger(__name__)

@require_POST
def update_cart_quantity(request, item_id):
    """
    Update the quantity of a specific cart item.
    """
    try:
        # Log request information for debugging
        logger.info(f"Received cart update request for item {item_id}")
        logger.info(f"POST data: {request.POST}")
        
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'message': 'User not authenticated'}, status=401)
        
        # Get the new quantity
        try:
            new_quantity = int(request.POST.get('quantity', 1))
        except ValueError:
            new_quantity = 1
            
        logger.info(f"Parsed quantity: {new_quantity}")
        
        # Get cart item
        cart_item = CartItem.objects.get(id=item_id, user=request.user)
        
        # Enforce constraints
        #the contraint for the quanitity < 1 is already enforced but just in case: 
        if new_quantity < 1:
            new_quantity = 1
            message = "Quantity cannot be less than 1"

        elif new_quantity > cart_item.product_variant.quantity:
            new_quantity = cart_item.product_variant.quantity
            message = f"Quantity adjusted to the maximum available stock ({new_quantity})"
        else:
            message = None
            
        # Update cart item
        cart_item.quantity = new_quantity
        cart_item.save()
        
        # Calculate new totals
        cart_items = CartItem.objects.filter(user=request.user)
        total = sum(item.subtotal() for item in cart_items)
        cart_total_quantity = sum(item.quantity for item in cart_items)
        
        # Prepare response
        response_data = {
            'success': True,
            'new_total': str(total),
            'adjusted_quantity': new_quantity 
        }
        
        if message:
            response_data['message'] = message
            
        logger.info(f"Response data: {response_data}")
        return JsonResponse(response_data)
        
    except CartItem.DoesNotExist:
        logger.error(f"Cart item {item_id} not found")
        return JsonResponse({'success': False, 'message': 'Cart item not found'}, status=404)
        
    except Exception as e:
        logger.error(f"Error in update_cart_quantity: {str(e)}")
        logger.error(traceback.format_exc())
        return JsonResponse({'success': False, 'message': str(e)}, status=500)
    
# Checkout
# shop/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import CartItem, Order, OrderedItem, ProductVariant
from django.http import JsonResponse
from decimal import Decimal

@login_required
def checkout(request):
    # Get user's cart items
    cart_items = CartItem.objects.filter(user=request.user)
    
    # Check if cart is empty
    if not cart_items.exists():
        messages.info(request, "Your cart is empty. Can't checkout an empty cart.")
        return redirect('shop:shop')
    
    context = {
        'cart_items': cart_items,
        'form_data': {},
        'form_errors': {}
    }
    
    # If there are form errors from a previous submission, add them to context
    if 'form_data' in request.session:
        context['form_data'] = request.session['form_data']
        del request.session['form_data']
    
    if 'form_errors' in request.session:
        context['form_errors'] = request.session['form_errors']
        del request.session['form_errors']
    
    return render(request, 'shop/checkout.html', context)

@login_required
def place_order(request):
    if request.method == 'POST':
        # Get form data
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        phone_country = request.POST.get('phone_country', '').strip()
        phone_number = request.POST.get('phone_number', '').strip()
        location = request.POST.get('location', '').strip()
        additional_info = request.POST.get('additional_info', '').strip()
        
        # Store form data for repopulating form if validation fails
        form_data = {
            'first_name': first_name,
            'last_name': last_name,
            'phone_country': phone_country,
            'phone_number': phone_number, 
            'location': location,
            'additional_info': additional_info
        }
        
        # Validate form data
        form_errors = {}
        
        if not first_name:
            form_errors['first_name'] = "Please enter your first name."
        
        if not last_name:
            form_errors['last_name'] = "Please enter your last name."
        
        if not phone_country:
            form_errors['phone_country'] = "Please enter a country code."
            
        if not phone_number:
            form_errors['phone_number'] = "Please enter your phone number."
        elif not phone_number.isdigit():
            form_errors['phone_number'] = "Phone number must contain only digits."
        
        if not location:
            form_errors['location'] = "Please enter your address."
        
        # If there are validation errors, return to checkout with errors
        if form_errors:
            request.session['form_data'] = form_data
            request.session['form_errors'] = form_errors
            return redirect('shop:checkout')
        
        # Get cart items
        cart_items = CartItem.objects.filter(user=request.user)
        
        # If cart is empty, redirect to shop
        if not cart_items.exists():
            messages.error(request, "Your cart is empty. Can't place an order.")
            return redirect('shop:shop')
        
        # Update user information
        user = request.user
        user.first_name = first_name
        user.last_name = last_name
        user.phone_number = f"{phone_country} {phone_number}"
        user.save()
        
        # Calculate total price
        total_price = sum(item.subtotal() for item in cart_items)
        
        # Create order
        order = Order.objects.create(
            user=user,
            location=location,
            total_price=total_price,
            additional_comment=additional_info
        )
        
        # Create ordered items and decrement product quantities
        for cart_item in cart_items:
            variant = cart_item.product_variant
            
            # Check if enough stock is available
            if variant.quantity < cart_item.quantity:
                messages.error(request, f"Sorry, not enough stock for {variant.product.title} in {variant.product_color.color.name} - {variant.size.name}.")
                order.delete()  # Delete the created order
                return redirect('shop:checkout')
            
            # Create ordered item
            OrderedItem.objects.create(
                order=order,
                product_variant=variant,
                quantity=cart_item.quantity,
                unit_price=variant.product.price
            )
            
            # Decrement product variant quantity
            variant.quantity -= cart_item.quantity
            variant.save()
        
        # Clear the cart
        cart_items.delete()
        
        
        return redirect(reverse('shop:shop') + '?order_success=true')
    
    return redirect('shop:checkout')

#Search
# Add this to your views.py
def search_products(request):
    query = request.GET.get('q', '')
    
    if query:
        # First search by title (higher priority)
        title_results = Product.objects.filter(title__icontains=query, hide=False)
        
        # Then search by description (lower priority)
        desc_results = Product.objects.filter(description__icontains=query, hide=False).exclude(title__icontains=query)
        
        # Combine results (title results come first)
        products = list(title_results) + list(desc_results)
        
        # Get all product colors for these products
        product_ids = [product.id for product in products]
        products_colors = ProductColor.objects.filter(product__id__in=product_ids, hide=False)
        
        # search by color name
        color_products_colors = ProductColor.objects.filter(
            color__name__icontains=query, 
            hide=False
        ).exclude(product__id__in=product_ids)
        
        # Combine all product colors
        products_colors = list(products_colors) + list(color_products_colors)
    else:
        products_colors = []
    
    context = {
        'query': query,
        'products_colors': products_colors,
    }
    
    return render(request, 'shop/search_results.html', context)

#Contact us

def contact(request):
    # Initialize variables
    name = ''
    email = ''
    
    # If user is logged in, prefill fields
    if request.user.is_authenticated:
        name = request.user.username
        email = request.user.email
    
    # Handle form submission
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        message_text = request.POST.get('message', '').strip()
        
        # Validate the form data
        if not name or not email or not message_text:
            messages.error(request, 'Name/Username, email, and message are all required')
        else:
            # Validate email using Django's validator
            try:
                validate_email(email)
                
                # Save the message to the database
                try:
                    Message.objects.create(name=name, email=email, message=message_text)
                    messages.success(request, 'Message sent successfully')
                    # Clear fields after successful submission if not logged in
                    if not request.user.is_authenticated:
                        name = ''
                        email = ''
                        # redirect after success
                        return redirect('shop:contactus')
                except Exception as e:
                    messages.error(request, f'Error sending message: {str(e)}')
            except ValidationError:
                messages.error(request, 'Invalid email format')
    
    context = {
        'name': name,
        'email': email
    }
    return render(request, 'shop/contactus.html', context)

#Wishlist
def wishlist_view(request):
    context = {}
    
    if request.user.is_authenticated:
        products_colors = ProductColor.objects.filter(
            wishlistitem__user=request.user
        ).select_related('product', 'color')
        context['products_colors'] = products_colors
    else:
        context['products_colors'] = [] 
        
    return render(request, 'shop/wishlist.html', context)

# Add or Remove from wishlist: 
def toggle_wishlist_item(request):
    if request.method == "POST":
        if not request.user.is_authenticated:
            return JsonResponse({'status': 'error', 'message': 'Please log in to use wishlist'})
        
        product_color_id = request.POST.get('product_id')
        
        try:
            product_color = get_object_or_404(ProductColor, id=product_color_id)
            
            # Check if item already exists in wishlist
            wishlist_item = WishlistItem.objects.filter(user=request.user, product_color=product_color)
            
            if wishlist_item.exists():
                # Remove from wishlist
                wishlist_item.delete()
                return JsonResponse({'status': 'success', 'action': 'removed'})
            # If the item didn't exist in the wishlist in the first place, add it
            else:
                # Add to wishlist
                WishlistItem.objects.create(user=request.user, product_color=product_color)
                return JsonResponse({'status': 'success', 'action': 'added'})
        #Handle the situation if something went wrong:         
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': 'Something went wrong'}, status=500)

# Notes: 
"""
1) select_related: 
ProductColor.objects.select_related('product', 'color').all()
This will fetch all product colors and join the product and color data using select_related. 
As if: 
SELECT * FROM productcolor
JOIN product ON productcolor.product_id = product.id

"""