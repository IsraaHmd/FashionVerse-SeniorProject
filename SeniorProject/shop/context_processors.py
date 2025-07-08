# In your app's context_processors.py file (create if it doesn't exist)
from .models import ProductVariant, CartItem


def cart_data(request):
    # Make sure you handle unauthenticated users properly
    if not request.user.is_authenticated:
        return {
            'cart_items': [],
            'total': 0,
            'cart_total_quantity': 0
        }
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
    
    # Calculate total
    total = sum(item.subtotal() for item in cart_items)
    
    # Get available sizes
    for item in cart_items:
        product_color = item.product_variant.product_color
        item.available_sizes = ProductVariant.objects.filter(
            product_color=product_color,
            hide=False,
            quantity__gt=0 # get the sizes that have quanitity>0
        ).select_related('size') #get the size of the product variant of this prod color, that is not hidden and has stock
    
    # Total quantity (including the total qunatity of each itemm)
    cart_total_quantity = sum(item.quantity for item in cart_items)
    # Handle cart message - get it, then clear it
    cart_message = None
    if 'cart_message' in request.session:
        cart_message = request.session['cart_message']
        del request.session['cart_message']

    return {
        'cart_items': cart_items,
        'total': total,
        'cart_total_quantity': cart_total_quantity,
        'cart_message': cart_message
    }
