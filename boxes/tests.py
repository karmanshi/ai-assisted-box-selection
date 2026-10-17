from decimal import Decimal

from django.test import TestCase

from .models import Order, OrderItem, Product, ShippingBox
from .recommender import product_fits_box, recommend_box


class BoxRecommendationTests(TestCase):
    def make_product(self, name="Book", length=10, width=8, height=2, weight=1):
        return Product.objects.create(
            name=name,
            length=length,
            width=width,
            height=height,
            weight=weight,
        )

    def make_box(
        self,
        name="Small",
        length=10,
        width=8,
        height=2,
        max_weight=5,
        cost="3.50",
    ):
        return ShippingBox.objects.create(
            name=name,
            length=length,
            width=width,
            height=height,
            max_weight=max_weight,
            cost=Decimal(cost),
        )

    def make_order(self, product=None, quantity=1):
        order = Order.objects.create()
        if product is not None:
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
            )
        return order

    def test_product_fits_when_rotated(self):
        product = self.make_product(length=8, width=10, height=2)
        box = self.make_box(length=10, width=8, height=2)

        self.assertTrue(product_fits_box(product, box))

    def test_recommends_lowest_cost_box_passing_all_checks(self):
        product = self.make_product()
        self.make_box(name="Too light", max_weight=0.5, cost="1.00")
        self.make_box(name="Too small", length=9, cost="1.50")
        self.make_box(name="Suitable but dearer", cost="5.00")
        cheapest = self.make_box(name="Cheapest suitable", cost="2.25")
        order = self.make_order(product)

        box, reason = recommend_box(order)

        self.assertEqual(box, cheapest)
        self.assertIn("lowest-cost", reason)
        self.assertIn("1.00 kg", reason)

    def test_boundary_dimensions_and_weight_are_accepted(self):
        product = self.make_product()
        box = self.make_box(max_weight=1)
        order = self.make_order(product)

        recommended, _ = recommend_box(order)

        self.assertEqual(recommended, box)

    def test_quantity_is_included_in_weight_and_volume(self):
        product = self.make_product(weight=2)
        self.make_box(max_weight=3, length=20, width=8, height=2)
        order = self.make_order(product, quantity=2)

        box, reason = recommend_box(order)

        self.assertIsNone(box)
        self.assertIn("weight", reason)

    def test_aggregate_product_volume_must_fit(self):
        product = self.make_product()
        self.make_box(length=10, width=8, height=3)
        order = self.make_order(product, quantity=2)

        box, reason = recommend_box(order)

        self.assertIsNone(box)
        self.assertIn("volume", reason)

    def test_empty_order_has_no_recommendation(self):
        order = self.make_order()

        box, reason = recommend_box(order)

        self.assertIsNone(box)
        self.assertIn("empty order", reason)

    def test_no_boxes_returns_explanation(self):
        order = self.make_order(self.make_product())

        box, reason = recommend_box(order)

        self.assertIsNone(box)
        self.assertIn("No box passed", reason)

    def test_equal_cost_uses_lowest_box_id(self):
        product = self.make_product()
        first = self.make_box(name="First")
        self.make_box(name="Second")
        order = self.make_order(product)

        box, _ = recommend_box(order)

        self.assertEqual(box, first)


class BoxSelectionViewTests(TestCase):
    def test_home_page_renders_dashboard(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "AI-Assisted Box Selection System")

    def test_dashboard_links_to_public_create_pages(self):
        response = self.client.get("/")

        self.assertContains(response, "/products/add/")
        self.assertContains(response, "/boxes/add/")
        self.assertContains(response, "/orders/add/")
        self.assertNotContains(response, "/admin/boxes/")

    def test_product_can_be_created_without_admin(self):
        response = self.client.post("/products/add/", {
            "name": "Notebook",
            "length": "20",
            "width": "15",
            "height": "2",
            "weight": "0.5",
        })

        self.assertRedirects(response, "/")
        self.assertTrue(Product.objects.filter(name="Notebook").exists())

    def test_product_form_rejects_nonpositive_dimensions(self):
        response = self.client.post("/products/add/", {
            "name": "Invalid",
            "length": "0",
            "width": "15",
            "height": "2",
            "weight": "0.5",
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Ensure this value is greater than or equal to 0.001")
        self.assertFalse(Product.objects.filter(name="Invalid").exists())

    def test_shipping_box_can_be_created_without_admin(self):
        response = self.client.post("/boxes/add/", {
            "name": "Large",
            "length": "30",
            "width": "20",
            "height": "10",
            "max_weight": "15",
            "cost": "12.50",
        })

        self.assertRedirects(response, "/")
        self.assertTrue(ShippingBox.objects.filter(name="Large").exists())

    def test_order_can_be_created_with_multiple_product_rows(self):
        first_product = Product.objects.create(
            name="Book", length=10, width=8, height=2, weight=1
        )
        second_product = Product.objects.create(
            name="Pen", length=12, width=1, height=1, weight=0.1
        )
        response = self.client.post("/orders/add/", {
            "items-TOTAL_FORMS": "2",
            "items-INITIAL_FORMS": "0",
            "items-MIN_NUM_FORMS": "1",
            "items-MAX_NUM_FORMS": "1000",
            "items-0-product": str(first_product.pk),
            "items-0-quantity": "2",
            "items-1-product": str(second_product.pk),
            "items-1-quantity": "1",
        })

        self.assertRedirects(response, "/")
        order = Order.objects.get()
        self.assertEqual(order.items.count(), 2)
        self.assertEqual(
            order.items.get(product=first_product).quantity,
            2,
        )

    def test_order_requires_a_product(self):
        response = self.client.post("/orders/add/", {
            "items-TOTAL_FORMS": "1",
            "items-INITIAL_FORMS": "0",
            "items-MIN_NUM_FORMS": "1",
            "items-MAX_NUM_FORMS": "1000",
            "items-0-product": "",
            "items-0-quantity": "1",
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Order.objects.count(), 0)

    def test_recommendation_page_renders_and_saves_result(self):
        product = Product.objects.create(
            name="Book",
            length=10,
            width=8,
            height=2,
            weight=1,
        )
        box = ShippingBox.objects.create(
            name="Small",
            length=10,
            width=8,
            height=2,
            max_weight=5,
            cost=Decimal("3.50"),
        )
        order = Order.objects.create()
        OrderItem.objects.create(order=order, product=product, quantity=1)

        response = self.client.get(f"/orders/{order.pk}/recommend/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Recommended Box: Small")
        order.refresh_from_db()
        self.assertEqual(order.recommended_box, box)
        self.assertTrue(order.recommendation_reason)

    def test_recommendation_for_unknown_order_returns_404(self):
        response = self.client.get("/orders/999/recommend/")

        self.assertEqual(response.status_code, 404)
