import base64
import json
import re
from io import BytesIO
from typing import Optional

from openai import OpenAI
from pydantic import BaseModel

from src.config import OPENAI_API_KEY, OPENAI_MODEL


class ExtractedDocument(BaseModel):
    document_type: str

    transaction_id: Optional[str] = None
    document_number: Optional[str] = None
    po_number: Optional[str] = None

    supplier: Optional[str] = None
    customer: Optional[str] = None
    date: Optional[str] = None

    item: Optional[str] = None

    quantity: Optional[float] = None
    quantity_delivered: Optional[float] = None

    unit_price: Optional[float] = None
    subtotal: Optional[float] = None
    vat_rate: Optional[float] = None
    vat: Optional[float] = None
    total: Optional[float] = None

    delivery_status: Optional[str] = None
    currency: Optional[str] = None


EXTRACTION_PROMPT = """
Extract the business document into JSON.

Return ONLY valid JSON with exactly these keys:

document_type
transaction_id
document_number
po_number
supplier
customer
date
item
quantity
quantity_delivered
unit_price
subtotal
vat_rate
vat
total
delivery_status
currency

Rules:

document_type must be one of:
invoice
purchase_order
delivery_receipt
unknown

Use document_number for:
- invoice number
- delivery number
- purchase order number when appropriate

Numeric amounts must be numbers without currency symbols.

Convert VAT percentages to decimal form.
Example: 23% becomes 0.23.

Use EUR when the document uses euros.

Use null when a field does not exist.

Do not invent missing information.
"""


def image_to_data_url(image):
    buffer = BytesIO()

    image.convert("RGB").save(
        buffer,
        format="JPEG",
        quality=90,
    )

    encoded = base64.b64encode(
        buffer.getvalue()
    ).decode("utf-8")

    return (
        "data:image/jpeg;base64,"
        + encoded
    )


def clean_json_output(text):
    text = text.strip()

    text = re.sub(
        r"^```(?:json)?\\s*",
        "",
        text,
        flags=re.IGNORECASE,
    )

    text = re.sub(
        r"\\s*```$",
        "",
        text,
    )

    return text.strip()


def extract_document(document):
    if not OPENAI_API_KEY:
        raise ValueError(
            "OPENAI_API_KEY is not configured."
        )

    client = OpenAI(
        api_key=OPENAI_API_KEY
    )

    content = [
        {
            "type": "input_text",
            "text": EXTRACTION_PROMPT,
        }
    ]

    if document["text"].strip():
        content.append(
            {
                "type": "input_text",
                "text": (
                    "DOCUMENT TEXT:\\n\\n"
                    + document["text"]
                ),
            }
        )

    else:
        content.append(
            {
                "type": "input_image",
                "image_url": image_to_data_url(
                    document["pages"][0]["image"]
                ),
            }
        )

    response = client.responses.create(
        model=OPENAI_MODEL,
        input=[
            {
                "role": "user",
                "content": content,
            }
        ],
    )

    raw = clean_json_output(
        response.output_text
    )

    data = json.loads(raw)

    return ExtractedDocument.model_validate(
        data
    )
