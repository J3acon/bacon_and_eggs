import io
import base64
from PyPDF2 import PdfReader


def main(pdf: bytes) -> dict:
    # Create a PdfReader instance
    reader = PdfReader(io.BytesIO(pdf))

    # Initialize an empty string to collect all the text
    full_text = ""

    # Iterate through all the pages and extract text
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            full_text += page_text + "\n"  # Add a newline character to separate pages

    # Encode the full text to a byte stream
    encoded_text = base64.b64encode(full_text.encode('utf-8')).decode('utf-8')

    # Return the file content and filename in the desired format
    return {
        "file": {
            "content": encoded_text,
            "filename": "content.txt"
        }
    }
