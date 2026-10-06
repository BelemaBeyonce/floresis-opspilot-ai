from fastapi import UploadFile


SUPPORTED_TEXT_TYPES = {
    "text/plain",
}


async def extract_text_from_upload(
    file: UploadFile,
) -> str:
    """
    Extract text from a supported uploaded file.
    """

    if file.content_type not in SUPPORTED_TEXT_TYPES:
        raise ValueError(
            f"Unsupported file type: {file.content_type}"
        )

    file_bytes = await file.read()

    if not file_bytes:
        raise ValueError("Uploaded file is empty")

    try:
        text = file_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError(
            "Unable to decode the uploaded text file as UTF-8"
        ) from exc

    text = text.strip()

    if not text:
        raise ValueError(
            "Uploaded file contains no readable text"
        )

    return text