from src.extraction import ExtractedDocument
from src.validation import validate_document


def test_valid_invoice():
    invoice = ExtractedDocument(
        document_type="invoice",
        transaction_id="TXN-001",
        document_number="INV-001",
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

    result = validate_document(invoice)

    assert result["valid"] is True
    assert result["issues"] == []


def test_invalid_financial_calculations():
    invoice = ExtractedDocument(
        document_type="invoice",
        transaction_id="TXN-BAD",
        document_number="INV-BAD",
        supplier="Supplier",
        customer="Customer",
        date="2026-09-21",
        item="Laptop",
        quantity=10,
        unit_price=100.0,
        subtotal=900.0,
        vat_rate=0.23,
        vat=100.0,
        total=950.0,
        currency="EUR",
    )

    result = validate_document(invoice)

    issue_types = {
        issue["type"]
        for issue in result["issues"]
    }

    assert result["valid"] is False
    assert "subtotal_mismatch" in issue_types
    assert "vat_mismatch" in issue_types
    assert "total_mismatch" in issue_types
