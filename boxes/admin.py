from django.contrib import admin
from .models import Product, ShippingBox, Order, OrderItem


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "length", "width", "height", "weight")


@admin.register(ShippingBox)
class ShippingBoxAdmin(admin.ModelAdmin):
    list_display = (
        "id", "name", "length", "width", "height", "max_weight", "cost"
    )


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "created_at", "recommended_box")
    inlines = [OrderItemInline]
# Register your models here.
