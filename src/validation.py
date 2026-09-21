from math import isclose


REQUIRED_FIELDS = {
    "invoice": [
        "transaction_id",
        "document_number",
        "supplier",
        "customer",
        "date",
        "item",
        "subtotal",
        "vat_rate",
        "vat",
        "total",
    ],
    "purchase_order": [
        "transaction_id",
        "document_number",
        "supplier",
        "customer",
        "date",
        "item",
        "quantity",
        "unit_price",
        "subtotal",
        "vat_rate",
        "vat",
        "total",
    ],
    "delivery_receipt": [
        "transaction_id",
        "document_number",
        "supplier",
        "customer",
        "date",
        "item",
        "quantity_delivered",
    ],
}


def validate_required_fields(document):
    missing = []

    required = REQUIRED_FIELDS.get(
        document.document_type,
        [],
    )

    for field in required:
        value = getattr(
            document,
            field,
            None,
        )

        if value is None or value == "":
            missing.append(field)

    return missing


def validate_subtotal(document):
    if (
        document.quantity is None
        or document.unit_price is None
        or document.subtotal is None
    ):
        return None

    expected = (
        document.quantity
        * document.unit_price
    )

    return {
        "valid": isclose(
            document.subtotal,
            expected,
            rel_tol=1e-6,
            abs_tol=0.01,
        ),
        "expected": round(expected, 2),
        "actual": round(
            document.subtotal,
            2,
        ),
    }


def validate_vat(document):
    if (
        document.subtotal is None
        or document.vat_rate is None
        or document.vat is None
    ):
        return None

    expected = (
        document.subtotal
        * document.vat_rate
    )

    return {
        "valid": isclose(
            document.vat,
            expected,
            rel_tol=1e-6,
            abs_tol=0.01,
        ),
        "expected": round(expected, 2),
        "actual": round(
            document.vat,
            2,
        ),
    }


def validate_total(document):
    if (
        document.subtotal is None
        or document.vat is None
        or document.total is None
    ):
        return None

    expected = (
        document.subtotal
        + document.vat
    )

    return {
        "valid": isclose(
            document.total,
            expected,
            rel_tol=1e-6,
            abs_tol=0.01,
        ),
        "expected": round(expected, 2),
        "actual": round(
            document.total,
            2,
        ),
    }


def validate_document(document):
    issues = []

    missing_fields = validate_required_fields(
        document
    )

    for field in missing_fields:
        issues.append(
            {
                "type": "missing_field",
                "field": field,
                "severity": "high",
                "message": (
                    f"Required field missing: {field}"
                ),
            }
        )

    subtotal_check = validate_subtotal(
        document
    )

    if (
        subtotal_check is not None
        and not subtotal_check["valid"]
    ):
        issues.append(
            {
                "type": "subtotal_mismatch",
                "severity": "high",
                "message": (
                    f"Subtotal mismatch: expected "
                    f"{subtotal_check['expected']}, "
                    f"found {subtotal_check['actual']}."
                ),
            }
        )

    vat_check = validate_vat(
        document
    )

    if (
        vat_check is not None
        and not vat_check["valid"]
    ):
        issues.append(
            {
                "type": "vat_mismatch",
                "severity": "high",
                "message": (
                    f"VAT mismatch: expected "
                    f"{vat_check['expected']}, "
                    f"found {vat_check['actual']}."
                ),
            }
        )

    total_check = validate_total(
        document
    )

    if (
        total_check is not None
        and not total_check["valid"]
    ):
        issues.append(
            {
                "type": "total_mismatch",
                "severity": "high",
                "message": (
                    f"Total mismatch: expected "
                    f"{total_check['expected']}, "
                    f"found {total_check['actual']}."
                ),
            }
        )

    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "checks": {
            "subtotal": subtotal_check,
            "vat": vat_check,
            "total": total_check,
        },
    }
