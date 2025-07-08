from django.conf import settings
from django.db import models
from colorfield.fields import ColorField
from django.core.exceptions import ValidationError
from django.utils.html import format_html
from decimal import Decimal

class Color(models.Model):
    name = models.CharField(max_length=50)
    hex_code = ColorField(default='#FFFFFF')  

    
    def color_preview(self):
        return format_html(
            '<div style="width: 30px; height: 30px; background-color: {}; border-radius: 50%;"></div>',
            self.hex_code
        )
    
    class Meta:
        ordering = ['name']
        
    def __str__(self):
        return f"{self.name} ({self.hex_code})"
    
class Size(models.Model):
    name = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.name
    class Meta:
        ordering = ['name'] 
# Products
class Product(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null= True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    hide = models.BooleanField(default=False)
    #The image is going to be in prodcut color since each color of the product has a different product image
    #Total stock below as if it's an attribute
    @property
    def total_stock(self):
        return sum(
            variant.quantity
            for color_variant in self.color_variants.all()  # Get all colors of this product
            for variant in color_variant.variants.all()  # Get all size variants of each color
        )

    
    def clean(self):
        """Ensure price is not negative and show a proper validation error in the form."""
        if not self.price or self.price < 0:
            raise ValidationError({'price': "Price must be a non-negative number."})
    def __str__(self):
        return f"{self.title}"
    #for sorting
    class Meta:
        ordering = ['title'] 
    
class ProductColor(models.Model):
    product = models.ForeignKey(Product, related_name='color_variants', on_delete=models.CASCADE)
    color = models.ForeignKey(Color, related_name='product_colors', on_delete=models.PROTECT)

    # Image can be either uploaded or from an external URL
    image_upload = models.ImageField(upload_to='product_images/', blank=True, null=True)
    image_url = models.URLField(blank=True, null=True)

    #hide to be used instead of delete
    hide = models.BooleanField(default=False)

    # We don't repeat the same color for the same product, so together they are unique
    class Meta:
        unique_together = ('product', 'color')

    
    #In case the user uploaded both image and url: 
    def get_image(self):
        """Returns the correct image URL to use in templates."""
        return self.image_url if self.image_url else self.image_upload.url if self.image_upload else ""
    #Calculate the total stock of this color
    @property
    def total_product_color_stock(self):
        # Check if variants exist, if not return 0
        if self.variants.exists():
            return sum(variant.quantity for variant in self.variants.all())
        return 0


    def __str__(self):
        return f"{self.product.title} - {self.color.name}"
    
#Product variant class: It's a class to keep track of the quantity of the product of different sizes and/or colors, color is not optional
class ProductVariant(models.Model):
    """
    Handles the combination of product, color, size, and quantity.
    Example: "Red - M - 10 pieces"
    """
    product_color = models.ForeignKey(ProductColor, related_name='variants', on_delete=models.CASCADE)
    size = models.ForeignKey(Size, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)
    hide = models.BooleanField(default=False)
    # Can't repeat the same size for the same color and same product: 
    class Meta:
            unique_together = ('product_color', 'size')
    #Ensure quantity is not negative and show a proper validation error in the form.
    def clean(self):
        
        if self.quantity is None or self.quantity < 0:
            raise ValidationError({'quantity': "Quantity must be a non-negative number."})

    def __str__(self):
        return f"{self.product_color.product.title} - {self.product_color.color.name} - {self.size.name} ({self.quantity} pcs)"

    # Below allows you to access the Product and Color fields directly from a ProductVariant instance. Example: (variant = ProductVariant.objects.get(id=1) print(variant.product.title))
    @property
    def product(self):
        return self.product_color.product

    @property
    def color(self):
        return self.product_color.color

# CartItems: the items that will be displayed in the user's cart

class CartItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product_variant = models.ForeignKey('ProductVariant', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'product_variant')  # Correct placement

    def clean(self):
        if not self.quantity or self.quantity < 1:
            #Quantity if attempted to be set less than 1 it will be set again to 1
            self.quantity = 1
            raise ValidationError("Quantity must be at least 1.")
        elif self.quantity > self.product_variant.quantity:
            raise ValidationError({"The maximum quantity of this item has been already added to the cart."})
   
    #Subtotal because it is the price*quantity of the item, the total is the total of all items in cart
    def subtotal(self):
        return Decimal(self.product_variant.product.price) * self.quantity

    def __str__(self):
        return f"{self.user.email} - {self.product_variant} ({self.quantity})"

#Order and Order Items


class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing','Processing'),
        ('completed', 'Completed'),
        ('canceled', 'Canceled'),
    )
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    location = models.CharField(max_length=255)  
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    ordered_at = models.DateTimeField(auto_now_add=True)
    additional_comment = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-ordered_at']  # Most recent orders first
    
    def __str__(self):
        return f"Order #{self.id} - {self.user.email} ({self.status})"
    
    def calculate_total(self):
        """Calculate the total price of all items in the order"""
        return sum(item.subtotal for item in self.items.all())
    
    def save(self, *args, **kwargs):
        # Update total price if it's a new order
        if not self.id:
            self.total_price = Decimal('0.00')
        super().save(*args, **kwargs)
        
        # Recalculate total after saving (for when items are added)
        if self.items.exists():
            self.total_price = self.calculate_total()
            super().save(update_fields=['total_price'])


class OrderedItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product_variant = models.ForeignKey('ProductVariant', on_delete=models.PROTECT)
    product = models.ForeignKey('Product', on_delete=models.PROTECT)  # Denormalization for easier querying
    product_color = models.ForeignKey('ProductColor', on_delete=models.PROTECT)  # Denormalization
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)  # Price at time of order (one item not quanitity*price of 1)
    
    class Meta:
        ordering = ['id']
    
    def __str__(self):
        return f"{self.quantity}x {self.product.title} - {self.product_color.color.name} ({self.product_variant.size.name})"
    
    @property
    def subtotal(self):
        """Calculate the total price for this line item"""
        return self.quantity * self.unit_price
    def clean(self):
        """Custom validation for OrderedItem"""
        if not self.quantity or self.quantity < 1:
            # If quantity is less than 1, set it to 1 and raise a validation error
            self.quantity = 1
            raise ValidationError("Quantity must be at least 1.")
        elif self.quantity > self.product_variant.quantity:
            # Ensure that the quantity doesn't exceed the available stock
            raise ValidationError("The maximum quantity of this item has already been added.")
        
        # Ensure that the price is valid (not negative or blank)
        if self.unit_price is None or self.unit_price < 0:
            raise ValidationError("Price can't be negative or blank.")
        
    def save(self, *args, **kwargs):
        #When a new item is added, get its product and prod color and add them and price too, and incase the product vairant is changed by the admin then those fields will change too
        self.product = self.product_variant.product
        self.product_color = self.product_variant.product_color
        self.clean()
        super().save(*args, **kwargs)
        
        # Update the order total price
        self.order.total_price = self.order.calculate_total()
        self.order.save(update_fields=['total_price'])

#Messages for contact us

class Message(models.Model):
    name = models.CharField(max_length=255, blank=False, null=False)
    email = models.EmailField(blank=False, null=False)
    message = models.TextField(blank=False, null=False)
    sent_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-sent_at']  # Sort by most recent first
        
    def __str__(self):
        return f"{self.name} - {self.email}"

#Wishlist
class WishlistItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wishlist')
    product_color = models.ForeignKey(ProductColor, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'product_color')  
        
    def __str__(self):
        return f"{self.user.email} - {self.product_color}"
