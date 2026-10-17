from django.db import models

# Create your models here.
class Product(models.Model):
    name = models.CharField(max_length=100)
    length = models.FloatField(help_text="Length in cm")
    width = models.FloatField(help_text="Width in cm")
    height = models.FloatField(help_text="Height in cm")
    weight = models.FloatField(help_text="Weight in kg")

    def __str__(self):
        return self.name 

class ShippingBox(models.Model):
    name = models.CharField(max_length=100)
    length = models.FloatField(help_text="Internal length in cm")
    width = models.FloatField(help_text="Internal width in cm")
    height = models.FloatField(help_text="Internal height in cm")
    max_weight = models.FloatField(help_text="Maximum weight in kg")
    cost = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    products = models.ManyToManyField(
        Product,
        through="OrderItem",
        related_name="orders",
    )
    recommended_box = models.ForeignKey(
        ShippingBox,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    recommendation_reason = models.TextField(blank=True)

    def __str__(self):
        return f"Order #{self.pk}"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"