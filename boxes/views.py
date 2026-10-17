from django.db import transaction
from django.shortcuts import get_object_or_404, render
from django.shortcuts import redirect

from .forms import OrderItemFormSet, ProductForm, ShippingBoxForm
from .models import Product, ShippingBox, Order
from .recommender import recommend_box


def home(request):
    orders = Order.objects.all().order_by("-id")

    return render(request, "homes.html", {
        "orders": orders,
        "products": Product.objects.all(),
        "boxes": ShippingBox.objects.all(),
    })


def add_product(request):
    form = ProductForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("home")

    return render(request, "add_record.html", {
        "form": form,
        "title": "Add Product",
        "submit_label": "Save Product",
    })


def add_shipping_box(request):
    form = ShippingBoxForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("home")

    return render(request, "add_record.html", {
        "form": form,
        "title": "Add Shipping Box",
        "submit_label": "Save Shipping Box",
    })


def create_order(request):
    formset = OrderItemFormSet(request.POST or None)
    if request.method == "POST" and formset.is_valid():
        with transaction.atomic():
            order = Order.objects.create()
            formset.instance = order
            formset.save()
        return redirect("home")

    return render(request, "create_order.html", {
        "formset": formset,
        "title": "Create Order",
    })


def recommend(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    box, reason = recommend_box(order)

    order.recommended_box = box
    order.recommendation_reason = reason
    order.save()

    return render(request, "recommendation.html", {
        "order": order,
        "box": box,
        "reason": reason,
    })