from itertools import combinations

from src.document_classifier import classify_document
from src.document_loader import load_document
from src.duplicate_detection import detect_duplicate
from src.extraction import extract_document
from src.matching import compare_transaction
from src.risk import calculate_risk
from src.validation import validate_document


class DocumentIntelligencePipeline:
    def process_documents(self, file_paths):
        processed = []

        for file_path in file_paths:
            loaded = load_document(file_path)

            classification = classify_document(
                loaded
            )

            extracted = extract_document(
                loaded
            )

            validation = validate_document(
                extracted
            )

            processed.append(
                {
                    "filename": loaded["filename"],
                    "classification": classification,
                    "extracted": extracted,
                    "validation": validation,
                }
            )

        purchase_orders = [
            item
            for item in processed
            if item["extracted"].document_type
            == "purchase_order"
        ]

        invoices = [
            item
            for item in processed
            if item["extracted"].document_type
            == "invoice"
        ]

        delivery_receipts = [
            item
            for item in processed
            if item["extracted"].document_type
            == "delivery_receipt"
        ]

        transaction_result = None

        if (
            len(purchase_orders) == 1
            and len(invoices) >= 1
            and len(delivery_receipts) == 1
        ):
            transaction_result = compare_transaction(
                purchase_orders[0]["extracted"],
                invoices[0]["extracted"],
                delivery_receipts[0]["extracted"],
            )

        duplicate_results = []

        for invoice_a, invoice_b in combinations(
            invoices,
            2,
        ):
            result = detect_duplicate(
                invoice_a["extracted"],
                invoice_b["extracted"],
            )

            duplicate_results.append(
                {
                    "invoice_a": invoice_a["filename"],
                    "invoice_b": invoice_b["filename"],
                    **result,
                }
            )

        strongest_duplicate = None

        if duplicate_results:
            strongest_duplicate = max(
                duplicate_results,
                key=lambda item: item["similarity"],
            )

        validation_results = [
            item["validation"]
            for item in processed
        ]

        risk = calculate_risk(
            validation_results=validation_results,
            transaction_result=transaction_result,
            duplicate_result=strongest_duplicate,
        )

        return {
            "documents": processed,
            "transaction_result": transaction_result,
            "duplicate_results": duplicate_results,
            "risk": risk,
        }
