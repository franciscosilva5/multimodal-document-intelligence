import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.duplicate_detection import detect_duplicate
from src.extraction import ExtractedDocument
from src.matching import compare_transaction
from src.risk import calculate_risk
from src.validation import validate_document


def create_transaction(
    invoice_price=100.0,
    delivered=10,
):
    po = ExtractedDocument(
        document_type="purchase_order",
        transaction_id="TXN-EVAL",
        document_number="PO-EVAL",
        po_number="PO-EVAL",
        supplier="Evaluation Supplier",
        customer="Evaluation Customer",
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

    invoice_subtotal = (
        10 * invoice_price
    )

    invoice_vat = (
        invoice_subtotal * 0.23
    )

    invoice = ExtractedDocument(
        document_type="invoice",
        transaction_id="TXN-EVAL",
        document_number="INV-EVAL",
        po_number="PO-EVAL",
        supplier="Evaluation Supplier",
        customer="Evaluation Customer",
        date="2026-09-21",
        item="Laptop",
        quantity=10,
        unit_price=invoice_price,
        subtotal=invoice_subtotal,
        vat_rate=0.23,
        vat=invoice_vat,
        total=invoice_subtotal + invoice_vat,
        currency="EUR",
    )

    delivery = ExtractedDocument(
        document_type="delivery_receipt",
        transaction_id="TXN-EVAL",
        document_number="DEL-EVAL",
        po_number="PO-EVAL",
        supplier="Evaluation Supplier",
        customer="Evaluation Customer",
        date="2026-09-22",
        item="Laptop",
        quantity_delivered=delivered,
    )

    return po, invoice, delivery


def main():
    passed = 0
    total = 0

    print(
        "\nMULTIMODAL DOCUMENT INTELLIGENCE EVALUATION"
    )
    print("=" * 60)

    po, invoice, delivery = create_transaction()

    total += 1
    result = compare_transaction(
        po,
        invoice,
        delivery,
    )
    ok = result["match"] is True
    passed += int(ok)
    print(
        "Clean transaction:",
        "PASS" if ok else "FAIL",
    )

    po, invoice, delivery = create_transaction(
        invoice_price=120.0,
        delivered=8,
    )

    total += 1
    result = compare_transaction(
        po,
        invoice,
        delivery,
    )

    fields = {
        item["field"]
        for item in result["mismatches"]
    }

    ok = (
        "unit_price" in fields
        and "delivery_quantity" in fields
    )

    passed += int(ok)

    print(
        "Cross-document anomalies:",
        "PASS" if ok else "FAIL",
    )

    total += 1

    bad_invoice = invoice.model_copy(
        deep=True
    )

    bad_invoice.vat = 1.0

    validation = validate_document(
        bad_invoice
    )

    types = {
        item["type"]
        for item in validation["issues"]
    }

    ok = "vat_mismatch" in types
    passed += int(ok)

    print(
        "Financial validation:",
        "PASS" if ok else "FAIL",
    )

    total += 1

    duplicate = invoice.model_copy(
        deep=True
    )

    duplicate.document_number = (
        invoice.document_number.replace(
            "-",
            "",
        )
    )

    duplicate_result = detect_duplicate(
        invoice,
        duplicate,
    )

    ok = duplicate_result[
        "is_duplicate"
    ]

    passed += int(ok)

    print(
        "Duplicate detection:",
        "PASS" if ok else "FAIL",
    )

    total += 1

    risk = calculate_risk(
        transaction_result=result
    )

    ok = (
        risk["review_required"] is True
    )

    passed += int(ok)

    print(
        "Human-review routing:",
        "PASS" if ok else "FAIL",
    )

    print("\n" + "=" * 60)

    print(
        f"Final result: "
        f"{passed}/{total} "
        f"({passed / total:.1%})"
    )


if __name__ == "__main__":
    main()
