from src.duplicate_detection import detect_duplicate
from src.extraction import ExtractedDocument
from src.matching import compare_transaction
from src.risk import calculate_risk


def make_documents():
    po = ExtractedDocument(
        document_type="purchase_order",
        transaction_id="TXN-001",
        document_number="PO-1001",
        po_number="PO-1001",
        supplier="Supplier",
        customer="Customer",
        date="2026-09-20",
        item="Laptop",
        quantity=10,
        unit_price=100.0,
        subtotal=1000.0,
        vat_rate=0.23,
        vat=230.0,
        total=1230.0,
        currency="EUR",
    )

    invoice = ExtractedDocument(
        document_type="invoice",
        transaction_id="TXN-001",
        document_number="INV-1001",
        po_number="PO-1001",
        supplier="Supplier",
        customer="Customer",
        date="2026-09-21",
        item="Laptop",
        quantity=10,
        unit_price=100.0,
        subtotal=1000.0,
        vat_rate=0.23,
        vat=230.0,
        total=1230.0,
        currency="EUR",
    )

    delivery = ExtractedDocument(
        document_type="delivery_receipt",
        transaction_id="TXN-001",
        document_number="DEL-1001",
        po_number="PO-1001",
        supplier="Supplier",
        customer="Customer",
        date="2026-09-22",
        item="Laptop",
        quantity_delivered=10,
    )

    return po, invoice, delivery


def test_consistent_transaction():
    po, invoice, delivery = make_documents()

    result = compare_transaction(
        po,
        invoice,
        delivery,
    )

    assert result["match"] is True
    assert result["mismatches"] == []


def test_quantity_mismatch():
    po, invoice, delivery = make_documents()

    delivery.quantity_delivered = 8

    result = compare_transaction(
        po,
        invoice,
        delivery,
    )

    fields = {
        item["field"]
        for item in result["mismatches"]
    }

    assert result["match"] is False
    assert "delivery_quantity" in fields


def test_duplicate_invoice_detection():
    _, invoice_a, _ = make_documents()

    invoice_b = invoice_a.model_copy(
        deep=True
    )

    invoice_b.document_number = "INV1001"

    result = detect_duplicate(
        invoice_a,
        invoice_b,
    )

    assert result["is_duplicate"] is True
    assert result["similarity"] >= 0.95


def test_high_risk_requires_review():
    result = calculate_risk(
        transaction_result={
            "mismatches": [
                {
                    "field": "unit_price",
                    "value_a": 100,
                    "value_b": 150,
                    "source_a": "purchase_order",
                    "source_b": "invoice",
                },
                {
                    "field": "delivery_quantity",
                    "value_a": 10,
                    "value_b": 5,
                    "source_a": "purchase_order",
                    "source_b": "delivery_receipt",
                },
                {
                    "field": "total",
                    "value_a": 1230,
                    "value_b": 1845,
                    "source_a": "purchase_order",
                    "source_b": "invoice",
                },
            ]
        }
    )

    assert result["risk_level"] == "high"
    assert result["review_required"] is True
