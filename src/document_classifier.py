import base64
from io import BytesIO

from openai import OpenAI

from src.config import OPENAI_API_KEY, OPENAI_MODEL


DOCUMENT_TYPES = {
    "invoice",
    "purchase_order",
    "delivery_receipt",
    "unknown",
}


def classify_from_text(text):
    normalized = text.lower()

    if "purchase order" in normalized:
        return {
            "document_type": "purchase_order",
            "method": "text_rules",
            "confidence": 1.0,
        }

    if "delivery receipt" in normalized:
        return {
            "document_type": "delivery_receipt",
            "method": "text_rules",
            "confidence": 1.0,
        }

    if "invoice" in normalized:
        return {
            "document_type": "invoice",
            "method": "text_rules",
            "confidence": 1.0,
        }

    return None


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

    return f"data:image/jpeg;base64,{encoded}"


def classify_from_image(image):
    if not OPENAI_API_KEY:
        raise ValueError(
            "OPENAI_API_KEY is not configured."
        )

    client = OpenAI(
        api_key=OPENAI_API_KEY
    )

    response = client.responses.create(
        model=OPENAI_MODEL,
        input=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": (
                            "Classify this business document. "
                            "Reply with exactly one value: "
                            "invoice, purchase_order, "
                            "delivery_receipt, or unknown."
                        ),
                    },
                    {
                        "type": "input_image",
                        "image_url": image_to_data_url(image),
                    },
                ],
            }
        ],
    )

    value = response.output_text.strip().lower()

    if value not in DOCUMENT_TYPES:
        value = "unknown"

    return {
        "document_type": value,
        "method": "vision_model",
        "confidence": None,
    }


def classify_document(document):
    if document["text"].strip():
        result = classify_from_text(
            document["text"]
        )

        if result is not None:
            return result

    return classify_from_image(
        document["pages"][0]["image"]
    )
