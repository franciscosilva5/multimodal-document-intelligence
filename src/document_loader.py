from pathlib import Path

import pymupdf
from PIL import Image


SUPPORTED_EXTENSIONS = {
    ".pdf",
    ".png",
    ".jpg",
    ".jpeg",
}


def load_pdf(path):
    document = pymupdf.open(path)

    pages = []
    text_parts = []

    for page_number, page in enumerate(document):
        text = page.get_text().strip()

        if text:
            text_parts.append(text)

        pixmap = page.get_pixmap(
            matrix=pymupdf.Matrix(1.5, 1.5),
            alpha=False,
        )

        image = Image.frombytes(
            "RGB",
            [pixmap.width, pixmap.height],
            pixmap.samples,
        )

        pages.append(
            {
                "page_number": page_number + 1,
                "image": image,
                "text": text,
            }
        )

    document.close()

    return {
        "document_type": "pdf",
        "page_count": len(pages),
        "text": "\n\n".join(text_parts),
        "pages": pages,
    }


def load_image(path):
    image = Image.open(path).convert("RGB")

    return {
        "document_type": "image",
        "page_count": 1,
        "text": "",
        "pages": [
            {
                "page_number": 1,
                "image": image,
                "text": "",
            }
        ],
    }


def load_document(file_path):
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Document not found: {path}"
        )

    extension = path.suffix.lower()

    if extension not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported document type: {extension}"
        )

    if extension == ".pdf":
        result = load_pdf(path)
    else:
        result = load_image(path)

    result.update(
        {
            "filename": path.name,
            "path": str(path),
            "extension": extension,
        }
    )

    return result
