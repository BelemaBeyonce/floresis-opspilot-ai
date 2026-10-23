from io import BytesIO

from fastapi import UploadFile
from pypdf import PdfReader


async def extract_text_from_upload(file: UploadFile) -> str:
    content = await file.read()

    if not content:
        raise ValueError("Uploaded file is empty")

    # Handle plain-text files
    if file.content_type == "text/plain":
        try:
            text = content.decode("utf-8")
        except UnicodeDecodeError:
            raise ValueError("Text file must use UTF-8 encoding")

    # Handle PDF files
    elif file.content_type == "application/pdf":
        try:
            pdf_reader = PdfReader(BytesIO(content))

            pages = []

            for page in pdf_reader.pages:
                page_text = page.extract_text() or ""
                pages.append(page_text)

            text = "\n".join(pages)

        except Exception as exc:
            raise ValueError(
                "Unable to read PDF file"
            ) from exc

    else:
        raise ValueError(
            f"Unsupported file type: {file.content_type}"
        )

    if not text.strip():
        raise ValueError(
            "Uploaded file contains no extractable text"
        )

    return text