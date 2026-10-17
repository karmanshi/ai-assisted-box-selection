from django import forms
from django.core.validators import MinValueValidator
from django.forms import inlineformset_factory

from .models import Order, OrderItem, Product, ShippingBox


class ProductForm(forms.ModelForm):
    length = forms.FloatField(
        min_value=0.001, label="Length (cm)"
    )
    width = forms.FloatField(
        min_value=0.001, label="Width (cm)"
    )
    height = forms.FloatField(
        min_value=0.001, label="Height (cm)"
    )
    weight = forms.FloatField(
        min_value=0.001, label="Weight (kg)"
    )

    class Meta:
        model = Product
        fields = ("name", "length", "width", "height", "weight")


class ShippingBoxForm(forms.ModelForm):
    length = forms.FloatField(
        min_value=0.001, label="Internal length (cm)"
    )
    width = forms.FloatField(
        min_value=0.001, label="Internal width (cm)"
    )
    height = forms.FloatField(
        min_value=0.001, label="Internal height (cm)"
    )
    max_weight = forms.FloatField(
        min_value=0.001, label="Maximum weight (kg)"
    )
    cost = forms.DecimalField(
        min_value=0, max_digits=10, decimal_places=2
    )

    class Meta:
        model = ShippingBox
        fields = (
            "name",
            "length",
            "width",
            "height",
            "max_weight",
            "cost",
        )


class OrderItemForm(forms.ModelForm):
    quantity = forms.IntegerField(
        min_value=1,
        validators=[MinValueValidator(1)],
    )

    class Meta:
        model = OrderItem
        fields = ("product", "quantity")


OrderItemFormSet = inlineformset_factory(
    Order,
    OrderItem,
    form=OrderItemForm,
    extra=1,
    min_num=1,
    validate_min=True,
    can_delete=False,
)
