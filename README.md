# AI-Assisted Box Selection System

A small Django application for managing products, shipping boxes, and orders,
then recommending the least expensive box that passes the system's feasibility
checks.

## Requirements

- Python 3.10 or newer
- Django 5.2.18 (installed from `requirements.txt`)

## Setup

From this directory, run:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open `http://127.0.0.1:8000/` for the dashboard. Use **Add Product**,
**Add Shipping Box**, and **Create Order** to manage data from the app without
logging in to the Django admin. Orders can include multiple products and
quantities. Select **Recommend Box** for an order on the dashboard to see its
recommendation. The Django admin remains available for administrative use.

Dimensions are entered in centimetres, weights in kilograms, and box costs in
the selected currency (displayed as rupees in the interface).

## Recommendation rules and limitations

The system filters out boxes that exceed the total order weight, have less
volume than the total product volume, or cannot fit any individual product in
any axis-aligned orientation. Among the remaining boxes it selects the lowest
cost, using the box ID to break cost ties.

This is a feasibility heuristic, not a three-dimensional packing solver. The
combined volume and per-product dimension checks do not prove that multiple
items can physically be arranged together inside a box. Review recommendations
before shipping, especially for multi-item orders.

## Tests

Install dependencies and run:

```powershell
python manage.py test boxes
```

Recorded test-run output is kept in [TEST_OUTPUT.md](./TEST_OUTPUT.md).

