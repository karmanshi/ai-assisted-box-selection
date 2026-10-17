from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("products/add/", views.add_product, name="add_product"),
    path("boxes/add/", views.add_shipping_box, name="add_shipping_box"),
    path("orders/add/", views.create_order, name="create_order"),
    path(
        "orders/<int:order_id>/recommend/",
        views.recommend,
        name="recommend",
    ),
]