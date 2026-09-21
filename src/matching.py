from math import isclose


def compare_values(
    field,
    value_a,
    value_b,
    label_a,
    label_b,
    tolerance=0.01,
):
    if value_a is None or value_b is None:
        return None

    if isinstance(value_a, (int, float)) and isinstance(
        value_b,
        (int, float),
    ):
        match = isclose(
            value_a,
            value_b,
            abs_tol=tolerance,
        )
    else:
        match = str(value_a).strip().lower() == str(value_b).strip().lower()

    return {
        "field": field,
        "match": match,
        "value_a": value_a,
        "value_b": value_b,
        "source_a": label_a,
        "source_b": label_b,
    }


def compare_transaction(
    purchase_order,
    invoice,
    delivery_receipt,
):
    comparisons = []

    pairs = [
        (
            purchase_order,
            invoice,
            "purchase_order",
            "invoice",
            [
                "transaction_id",
                "po_number",
                "supplier",
                "customer",
                "item",
                "quantity",
                "unit_price",
                "subtotal",
                "vat_rate",
                "vat",
                "total",
            ],
        ),
        (
            purchase_order,
            delivery_receipt,
            "purchase_order",
            "delivery_receipt",
            [
                "transaction_id",
                "po_number",
                "supplier",
                "customer",
                "item",
            ],
        ),
    ]

    for (
        doc_a,
        doc_b,
        label_a,
        label_b,
        fields,
    ) in pairs:
        for field in fields:
            result = compare_values(
                field,
                getattr(doc_a, field, None),
                getattr(doc_b, field, None),
                label_a,
                label_b,
            )

            if result is not None:
                comparisons.append(result)

    quantity_check = None

    if (
        purchase_order.quantity is not None
        and delivery_receipt.quantity_delivered is not None
    ):
        quantity_check = {
            "field": "delivery_quantity",
            "match": isclose(
                purchase_order.quantity,
                delivery_receipt.quantity_delivered,
                abs_tol=0.01,
            ),
            "ordered": purchase_order.quantity,
            "delivered": delivery_receipt.quantity_delivered,
        }

    mismatches = [
        comparison
        for comparison in comparisons
        if not comparison["match"]
    ]

    if (
        quantity_check is not None
        and not quantity_check["match"]
    ):
        mismatches.append(
            {
                "field": "delivery_quantity",
                "match": False,
                "value_a": quantity_check["ordered"],
                "value_b": quantity_check["delivered"],
                "source_a": "purchase_order",
                "source_b": "delivery_receipt",
            }
        )

    return {
        "match": len(mismatches) == 0,
        "comparisons": comparisons,
        "mismatches": mismatches,
    }
