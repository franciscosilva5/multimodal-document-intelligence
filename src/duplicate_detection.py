import re
from difflib import SequenceMatcher


def normalize_identifier(value):
    if value is None:
        return ""

    return re.sub(
        r"[^a-zA-Z0-9]",
        "",
        str(value),
    ).lower()


def normalize_text(value):
    if value is None:
        return ""

    return re.sub(
        r"\s+",
        " ",
        str(value).strip().lower(),
    )


def text_similarity(value_a, value_b):
    a = normalize_text(value_a)
    b = normalize_text(value_b)

    if not a or not b:
        return 0.0

    return SequenceMatcher(
        None,
        a,
        b,
    ).ratio()


def identifier_similarity(value_a, value_b):
    a = normalize_identifier(value_a)
    b = normalize_identifier(value_b)

    if not a or not b:
        return 0.0

    if a == b:
        return 1.0

    return SequenceMatcher(
        None,
        a,
        b,
    ).ratio()


def numeric_similarity(value_a, value_b):
    if value_a is None or value_b is None:
        return 0.0

    if value_a == value_b:
        return 1.0

    maximum = max(
        abs(value_a),
        abs(value_b),
        1.0,
    )

    difference = abs(
        value_a - value_b
    )

    return max(
        0.0,
        1.0 - difference / maximum,
    )


def detect_duplicate(
    invoice_a,
    invoice_b,
    threshold=0.85,
):
    components = {
        "document_number": identifier_similarity(
            invoice_a.document_number,
            invoice_b.document_number,
        ),
        "supplier": text_similarity(
            invoice_a.supplier,
            invoice_b.supplier,
        ),
        "total": numeric_similarity(
            invoice_a.total,
            invoice_b.total,
        ),
        "date": (
            1.0
            if invoice_a.date
            and invoice_a.date == invoice_b.date
            else 0.0
        ),
        "po_number": identifier_similarity(
            invoice_a.po_number,
            invoice_b.po_number,
        ),
    }

    weights = {
        "document_number": 0.35,
        "supplier": 0.20,
        "total": 0.20,
        "date": 0.15,
        "po_number": 0.10,
    }

    score = sum(
        components[field] * weights[field]
        for field in weights
    )

    reasons = [
        field
        for field, similarity in components.items()
        if similarity >= 0.95
    ]

    return {
        "is_duplicate": score >= threshold,
        "similarity": round(score, 3),
        "components": components,
        "reasons": reasons,
    }
