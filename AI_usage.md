# AI usage

## AI tool used

I used ChatGPT for the completion of this project

## Prompts

#### User Prompt:
> How should I create the recommendation? I have created Product, Orders and box creation already. Give me the recommendation() function only
#### Output:
``` python
def recommendation(order):
    items = order.items.select_related("product")
    boxes = ShippingBox.objects.all()

    if not items.exists():
        return None

    total_weight = sum(
        item.product.weight * item.quantity
        for item in items
    )

    total_volume = sum(
        item.product.length
        * item.product.width
        * item.product.height
        * item.quantity
        for item in items
    )

    suitable_boxes = []

    for box in boxes:
        box_volume = box.length * box.width * box.height

        if total_weight > box.max_weight:
            continue

        if total_volume > box_volume:
            continue

        fits = True

        for item in items:
            product = item.product

            product_dimensions = sorted([
                product.length,
                product.width,
                product.height,
            ])

            box_dimensions = sorted([
                box.length,
                box.width,
                box.height,
            ])

            if not all(
                p <= b
                for p, b in zip(product_dimensions, box_dimensions)
            ):
                fits = False
                break

        if fits:
            suitable_boxes.append(box)

    if not suitable_boxes:
        return None

    return min(suitable_boxes, key=lambda box: box.cost)
```
How it works:
- Calculates total order weight and volume, including quantities.
- Rejects boxes that exceed the weight or volume limits.
- Checks whether each product individually fits inside the box, allowing rotation.
- Returns the lowest-cost suitable box, or None if no box passes the checks.
- Note: This is a basic heuristic. It doesn't guarantee that multiple products can physically fit together in the same box.

#### User Prompt:
> I have created templates for order creation, box creation and product creation, How should I organize recommend box UI
#### Output:
Here is the complete updated recommendation.html. It displays the order details, product dimensions and quantities, the recommended box, its cost, and the reason for selection. It also handles the case when no suitable box is found.
Save it as templates/recommendation.html (or in your existing template directory).

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <title>Box Recommendation</title>

    <style>
        * {
            box-sizing: border-box;
        }

        body {
            font-family: Arial, sans-serif;
            max-width: 850px;
            margin: 40px auto;
            padding: 0 20px;
            background: #f5f7fb;
            color: #222;
        }

        h1 {
            text-align: center;
            color: #1f2937;
        }

        .subtitle {
            text-align: center;
            color: #666;
            margin-bottom: 30px;
        }

        .card {
            background: white;
            padding: 25px;
            margin: 20px 0;
            border-radius: 10px;
            box-shadow: 0 2px 8px #00000012;
        }

        .success {
            border-left: 5px solid #198754;
        }

        .warning {
            border-left: 5px solid #d97706;
        }

        h2 {
            margin-top: 0;
        }

        .success h2 {
            color: #198754;
        }

        .warning h2 {
            color: #b45309;
        }

        .details {
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 15px;
        }

        .detail-item {
            background: #f8fafc;
            padding: 15px;
            border-radius: 7px;
        }

        .detail-item strong {
            display: block;
            margin-bottom: 7px;
            color: #555;
            font-size: 14px;
        }

        .detail-item span {
            font-size: 17px;
            font-weight: bold;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }

        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #e5e7eb;
        }

        th {
            background: #f3f4f6;
        }

        .reason {
            background: #f0fdf4;
            padding: 15px;
            border-radius: 7px;
            line-height: 1.6;
        }

        .button {
            display: inline-block;
            background: #2457d6;
            color: white;
            padding: 11px 18px;
            border-radius: 6px;
            text-decoration: none;
            margin-top: 10px;
        }

        .button:hover {
            background: #1d43a5;
        }

        .footer {
            text-align: center;
            margin: 30px 0;
        }

        @media (max-width: 600px) {
            .details {
                grid-template-columns: 1fr;
            }

            .card {
                padding: 18px;
            }

            th, td {
                padding: 8px;
                font-size: 13px;
            }
        }
    </style>
</head>

<body>

    <h1>Box Recommendation</h1>

    <p class="subtitle">
        Find the most suitable shipping box for your order.
    </p>

    <!-- Order details -->
    <div class="card">
        <h2>Order #{{ order.id }}</h2>

        <p>
            <strong>Created:</strong>
            {{ order.created_at|date:"d M Y, h:i A" }}
        </p>

        <h3>Products in this order</h3>

        <table>
            <thead>
                <tr>
                    <th>Product</th>
                    <th>Quantity</th>
                    <th>Dimensions (cm)</th>
                    <th>Weight Each (kg)</th>
                </tr>
            </thead>

            <tbody>
                {% for item in order.items.all %}
                    <tr>
                        <td>{{ item.product.name }}</td>
                        <td>{{ item.quantity }}</td>
                        <td>
                            {{ item.product.length }} ×
                            {{ item.product.width }} ×
                            {{ item.product.height }}
                        </td>
                        <td>{{ item.product.weight }}</td>
                    </tr>
                {% empty %}
                    <tr>
                        <td colspan="4">
                            This order has no products.
                        </td>
                    </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>

    <!-- Recommendation result -->
    {% if box %}

        <div class="card success">
            <h2>Recommended Box: {{ box.name }}</h2>

            <p>
                This box passed the recommendation checks and was
                selected based on the lowest cost among eligible boxes.
            </p>

            <div class="details">

                <div class="detail-item">
                    <strong>Box Dimensions</strong>
                    <span>
                        {{ box.length }} ×
                        {{ box.width }} ×
                        {{ box.height }} cm
                    </span>
                </div>

                <div class="detail-item">
                    <strong>Maximum Weight</strong>
                    <span>{{ box.max_weight }} kg</span>
                </div>

                <div class="detail-item">
                    <strong>Box Cost</strong>
                    <span>₹{{ box.cost }}</span>
                </div>

                <div class="detail-item">
                    <strong>Recommendation Status</strong>
                    <span>Suitable</span>
                </div>

            </div>

            <h3>Reason for Recommendation</h3>

            <div class="reason">
                {{ reason }}
            </div>

            <p>
                <strong>Note:</strong>
                The current algorithm checks individual product
                dimensions, total product volume, and total weight.
                It does not guarantee that multiple products can
                physically fit together in the box.
            </p>
        </div>

    {% else %}

        <div class="card warning">
            <h2>No Suitable Box Found</h2>

            <p>
                {{ reason|default:"No available box satisfies the current recommendation checks." }}
            </p>

            <p>
                You can try adding a larger box, checking product
                dimensions, or reviewing the order's total weight.
            </p>
        </div>

    {% endif %}

    <!-- Navigation -->
    <div class="footer">
        <a href="{% url 'home' %}" class="button">
            Back to Dashboard
        </a>

        <a href="/admin/" class="button">
            Manage Products and Boxes
        </a>
    </div>

</body>
</html>
```

## Output rejected or modified

I did not reject any of the documentation content. I kept the descriptions
limited to behavior visible in the app's views, templates, recommender, and
tests, and wrote them in this file rather than changing application code.

## Mistakes made by the AI

The form were being rendered twice by default in `recommendation.html`
