from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = ROOT / "data" / "generated"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


DOCUMENTS = [
    {
        "filename": "txn001_purchase_order.pdf",
        "title": "PURCHASE ORDER",
        "fields": [
            ("Transaction ID", "TXN-001"),
            ("PO Number", "PO-1001"),
            ("Supplier", "NovaTech Supplies Ltd."),
            ("Customer", "Atlas Consulting SA"),
            ("Date", "2026-09-10"),
            ("Item", "Business Laptop"),
            ("Quantity", "10"),
            ("Unit Price", "800.00 EUR"),
            ("Subtotal", "8000.00 EUR"),
            ("VAT Rate", "23%"),
            ("VAT", "1840.00 EUR"),
            ("Total", "9840.00 EUR"),
        ],
    },
    {
        "filename": "txn001_invoice.pdf",
        "title": "INVOICE",
        "fields": [
            ("Transaction ID", "TXN-001"),
            ("Invoice Number", "INV-2001"),
            ("PO Number", "PO-1001"),
            ("Supplier", "NovaTech Supplies Ltd."),
            ("Customer", "Atlas Consulting SA"),
            ("Date", "2026-09-11"),
            ("Item", "Business Laptop"),
            ("Quantity", "10"),
            ("Unit Price", "800.00 EUR"),
            ("Subtotal", "8000.00 EUR"),
            ("VAT Rate", "23%"),
            ("VAT", "1840.00 EUR"),
            ("Total", "9840.00 EUR"),
        ],
    },
    {
        "filename": "txn001_delivery_receipt.pdf",
        "title": "DELIVERY RECEIPT",
        "fields": [
            ("Transaction ID", "TXN-001"),
            ("Delivery Number", "DEL-3001"),
            ("PO Number", "PO-1001"),
            ("Supplier", "NovaTech Supplies Ltd."),
            ("Customer", "Atlas Consulting SA"),
            ("Date", "2026-09-13"),
            ("Item", "Business Laptop"),
            ("Quantity Delivered", "10"),
            ("Status", "Delivered in full"),
        ],
    },
    {
        "filename": "txn002_purchase_order.pdf",
        "title": "PURCHASE ORDER",
        "fields": [
            ("Transaction ID", "TXN-002"),
            ("PO Number", "PO-1002"),
            ("Supplier", "EuroOffice Systems Ltd."),
            ("Customer", "Atlas Consulting SA"),
            ("Date", "2026-09-14"),
            ("Item", "27-inch Monitor"),
            ("Quantity", "20"),
            ("Unit Price", "300.00 EUR"),
            ("Subtotal", "6000.00 EUR"),
            ("VAT Rate", "23%"),
            ("VAT", "1380.00 EUR"),
            ("Total", "7380.00 EUR"),
        ],
    },
    {
        "filename": "txn002_invoice.pdf",
        "title": "INVOICE",
        "fields": [
            ("Transaction ID", "TXN-002"),
            ("Invoice Number", "INV-2002"),
            ("PO Number", "PO-1002"),
            ("Supplier", "EuroOffice Systems Ltd."),
            ("Customer", "Atlas Consulting SA"),
            ("Date", "2026-09-15"),
            ("Item", "27-inch Monitor"),
            ("Quantity", "20"),
            ("Unit Price", "340.00 EUR"),
            ("Subtotal", "6800.00 EUR"),
            ("VAT Rate", "23%"),
            ("VAT", "1564.00 EUR"),
            ("Total", "8364.00 EUR"),
        ],
    },
    {
        "filename": "txn002_delivery_receipt.pdf",
        "title": "DELIVERY RECEIPT",
        "fields": [
            ("Transaction ID", "TXN-002"),
            ("Delivery Number", "DEL-3002"),
            ("PO Number", "PO-1002"),
            ("Supplier", "EuroOffice Systems Ltd."),
            ("Customer", "Atlas Consulting SA"),
            ("Date", "2026-09-17"),
            ("Item", "27-inch Monitor"),
            ("Quantity Delivered", "18"),
            ("Status", "Partial delivery"),
        ],
    },
]


def create_pdf(document):
    path = OUTPUT_DIR / document["filename"]

    pdf = canvas.Canvas(
        str(path),
        pagesize=A4,
    )

    width, height = A4

    pdf.setFont("Helvetica-Bold", 20)
    pdf.drawString(
        60,
        height - 70,
        document["title"],
    )

    pdf.setFont("Helvetica", 11)

    y = height - 120

    for key, value in document["fields"]:
        pdf.setFont("Helvetica-Bold", 10)
        pdf.drawString(60, y, f"{key}:")

        pdf.setFont("Helvetica", 10)
        pdf.drawString(210, y, value)

        y -= 28

    pdf.setFont("Helvetica-Oblique", 8)
    pdf.drawString(
        60,
        50,
        "Synthetic document generated for AI portfolio evaluation.",
    )

    pdf.save()

    print("Created:", path.name)


def create_image_sample():
    width = 1200
    height = 1500

    image = Image.new(
        "RGB",
        (width, height),
        "white",
    )

    draw = ImageDraw.Draw(image)

    draw.text(
        (80, 80),
        "INVOICE",
        fill="black",
    )

    lines = [
        "Transaction ID: TXN-003",
        "Invoice Number: INV-2003",
        "Supplier: Iberia Cloud Services",
        "Customer: Atlas Consulting SA",
        "Date: 2026-09-18",
        "Service: Cloud Infrastructure",
        "Quantity: 1",
        "Subtotal: 2500.00 EUR",
        "VAT Rate: 23%",
        "VAT: 575.00 EUR",
        "Total: 3075.00 EUR",
    ]

    y = 170

    for line in lines:
        draw.text(
            (80, y),
            line,
            fill="black",
        )
        y += 70

    path = OUTPUT_DIR / "txn003_invoice_image.png"
    image.save(path)

    print("Created:", path.name)


def main():
    for document in DOCUMENTS:
        create_pdf(document)

    create_image_sample()

    print(
        f"\nGenerated {len(DOCUMENTS) + 1} documents."
    )


if __name__ == "__main__":
    main()
