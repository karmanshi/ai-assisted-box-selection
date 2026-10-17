
from .models import ShippingBox


def get_volume(length, width, height):
    """Return volume in cubic centimetres."""
    return length * width * height


def product_fits_box(product, box):
    """Check whether one product fits in a box in some orientation."""
    product_dimensions = sorted(
        [product.length, product.width, product.height]
    )
    box_dimensions = sorted(
        [box.length, box.width, box.height]
    )

    return all(
        product_dim <= box_dim
        for product_dim, box_dim in zip(
            product_dimensions, box_dimensions
        )
    )


def recommend_box(order):
    """
    Return the lowest-cost box passing the basic feasibility checks.

    Limitation: this does not simulate the placement of multiple items.
    """
    items = list(order.items.select_related("product"))

    if not items:
        return None, "Cannot recommend a box for an empty order."

    total_weight = sum(
        item.product.weight * item.quantity
        for item in items
    )

    total_volume = sum(
        get_volume(
            item.product.length,
            item.product.width,
            item.product.height,
        ) * item.quantity
        for item in items
    )

    suitable_boxes = []

    for box in ShippingBox.objects.all():
        box_volume = get_volume(
            box.length, box.width, box.height
        )

        if total_weight > box.max_weight:
            continue

        if total_volume > box_volume:
            continue

        if not all(
            product_fits_box(item.product, box)
            for item in items
        ):
            continue

        suitable_boxes.append(box)

    if not suitable_boxes:
        return None, (
            "No box passed the individual dimension, total volume, "
            "and weight checks. Check the order or add another box."
        )

    best_box = min(
        suitable_boxes,
        key=lambda box: (box.cost, box.pk),
    )

    reason = (
        f"{best_box.name} is the lowest-cost box among those that "
        f"passed the basic checks. Total weight: {total_weight:.2f} kg. "
        f"Total product volume: {total_volume:.2f} cm³. "
        f"Box cost: ₹{best_box.cost}."
    )

    return best_box, reason
