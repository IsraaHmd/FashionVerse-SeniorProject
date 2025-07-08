from django.contrib import admin
from .models import *
# Register your models here.


# Inline for ProductVariant to add size and color within the product form
class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1  # Add an empty form for creating a new variant
    fields = ('size', 'quantity')  # Show fields for color, size, and quantity

# Inline for ProductColor (to add colors inside Product form)
class ProductColorInline(admin.TabularInline):
    model = ProductColor
    extra = 1  # Empty form for adding a new color
    fields = ('color', 'image_upload', 'image_url')  # Fields to display for colors
    inlines = [ProductVariantInline]  # Add ProductVariant inline within ProductColor

# Register Product admin
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'total_stock', 'hide', 'created_at') 
    inlines = [ProductColorInline]  # Allow creating Productcolors in the Product form
    search_fields = ('title', 'description')
    search_help_text = "Search by product title or description"
    list_filter = ('hide', 'created_at')
    ordering = ('title',)

#Color
class ColorAdmin(admin.ModelAdmin):
    # This will display the color preview in the list view
    list_display = ('name', 'hex_code', 'color_preview')
    search_fields = ('name', 'hex_code')
    search_help_text = "Search by color name or hex code"
    # To Make the color preview a clickable link that opens the full object
    def color_preview(self, obj):
        return format_html('<div style="width: 30px; height: 20px; background-color: {}"></div>', obj.hex_code)
    color_preview.short_description = 'Color Preview'  # Custom header for the column

#Size
class SizeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    search_help_text = "Search by size name"
    ordering = ('name',)

#Product Color Admin
class ProductColorAdmin(admin.ModelAdmin):
    list_display = ('product', 'color', 'hide', 'image_upload', 'image_url')
    inlines = [ProductVariantInline] 
    search_fields = ('product__title', 'color__name')
    search_help_text = "Search by product title or color name"
    list_filter = ('hide', 'color')
    ordering = ('product__title', 'color__name')

#Product Variant
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ('product_color', 'size', 'quantity','hide')
    search_fields = ('product_color__product__title', 'product_color__color__name', 'size__name')
    search_help_text = "Search by product title, color name, or size"
    list_filter = ('hide', 'size')
    ordering = ('product_color__product__title',)

    readonly_fields = ('product', 'color')
    def product(self, obj):
        return obj.product_color.product.title  
    product.short_description = "Product Choosen"

    def color(self, obj):
        return obj.product_color.color.name  
    color.short_description = "Color of this Product"

#Cart
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('user_email', 'product_name', 'color_size', 'quantity', 'subtotal_display', 'added_at')
    search_fields = ('user__email', 'user__username', 'product_variant__product_color__product__title')
    search_help_text = "Search by user email, username, or product title"
    list_filter = ('added_at', 'product_variant__size')
    ordering = ('-added_at',)
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'User'
    
    def product_name(self, obj):
        return obj.product_variant.product_color.product.title
    product_name.short_description = 'Product'
    
    def color_size(self, obj):
        return f"{obj.product_variant.product_color.color.name} - {obj.product_variant.size.name}"
    color_size.short_description = 'Color & Size'
    
    def subtotal_display(self, obj):
        return f"${obj.subtotal():.2f}"
    subtotal_display.short_description = 'Subtotal'
# Orders
class OrderedItemInline(admin.TabularInline):
    model = OrderedItem
    extra = 0
    fields = ('product_variant', 'quantity', 'unit_price')
    readonly_fields = ('quantity', 'unit_price',)

class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'user_email', 'status', 'total_items', 'total_price_display', 'ordered_at', 'location')
    search_fields = ('user__email', 'user__username', 'location', 'additional_comment')
    search_help_text = "Search by customer email, username, location, or comments"
    list_filter = ('status', 'ordered_at')
    ordering = ('-ordered_at',)
    inlines = [OrderedItemInline]
    
    def order_number(self, obj):
        return f"Order #{obj.id}"
    order_number.short_description = 'Order #'
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'Customer'
    
    def total_items(self, obj):
        return obj.items.count()
    total_items.short_description = 'Total Items'
    
    def total_price_display(self, obj):
        return f"${obj.total_price:.2f}"
    total_price_display.short_description = 'Total'

class OrderedItemAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'product_details', 'quantity', 'unit_price_display', 'subtotal_display')
    search_fields = ('order__id', 'product__title', 'product_color__color__name')
    search_help_text = "Search by order ID, product title, or color name"
    list_filter = ('order__status', 'product_variant__size')
    ordering = ('-order__ordered_at',)
    
    def order_number(self, obj):
        return f"Order #{obj.order.id}"
    order_number.short_description = 'Order #'
    
    def product_details(self, obj):
        return f"{obj.product.title} ({obj.product_color.color.name} - {obj.product_variant.size.name})"
    product_details.short_description = 'Product Details'
    
    def unit_price_display(self, obj):
        return f"${obj.unit_price:.2f}"
    unit_price_display.short_description = 'Unit Price'
    
    def subtotal_display(self, obj):
        return f"${obj.subtotal:.2f}"
    subtotal_display.short_description = 'Subtotal'

# Message    
class MessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'sent_at')
    list_filter = ('sent_at',)
    search_fields = ('name', 'email', 'message')
    search_help_text = "Search by name, email, or message content"
    ordering = ('-sent_at',)
#Wishlist
class WishlistItemAdmin(admin.ModelAdmin):
    list_display = ('user_email', 'product_name', 'color_name', 'added_at')
    search_fields = ('user__email', 'user__username', 'product_color__product__title', 'product_color__color__name')
    search_help_text = "Search by user email, username, product title, or color name"
    list_filter = ('added_at',)
    ordering = ('-added_at',)
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'User'
    
    def product_name(self, obj):
        return obj.product_color.product.title
    product_name.short_description = 'Product'
    
    def color_name(self, obj):
        return obj.product_color.color.name
    color_name.short_description = 'Color'

#Registering the models in admin
admin.site.register(Product, ProductAdmin)
admin.site.register(Color, ColorAdmin)
admin.site.register(Size, SizeAdmin)
admin.site.register(ProductVariant, ProductVariantAdmin)
admin.site.register(ProductColor,ProductColorAdmin)
admin.site.register(CartItem, CartItemAdmin)
admin.site.register(OrderedItem, OrderedItemAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Message, MessageAdmin)
admin.site.register(WishlistItem, WishlistItemAdmin)