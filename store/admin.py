from django.contrib import admin
from django.contrib.auth.models import User
from .models import (
    Web,
    Message,
    Address,
    Product,
    ProductImage,
    Order,
    OrderItem
)


# Register your models here.
class OrderItemInline(admin.TabularInline):
    model = OrderItem


class OrderAdmin(admin.ModelAdmin):
    list_display = ('date_ordered', 'customer', 'order_status', 'order_remarks', 'transaction_id')
    inlines = [
        OrderItemInline,
    ]


class UserAddressInline(admin.StackedInline):
    model = Address


class UserAdmin(admin.ModelAdmin):
    inlines = [
        UserAddressInline
    ]


class ProductImageInline(admin.StackedInline):
    model = ProductImage


class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock')
    inlines = [
        ProductImageInline
    ]


class MessageAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'message')


admin.site.register(Web)

admin.site.register(Message, MessageAdmin)

admin.site.register(Product, ProductAdmin)
admin.site.register(Order, OrderAdmin)

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
