
from PyPDF2 import PdfReader
from docx import Document
import io


def extract_resume_text(uploaded_file):
    """
    Extract text from an uploaded PDF or DOCX resume.
    """

    if uploaded_file is None:
        return ""

    file_name = uploaded_file.name.lower()

    try:
        uploaded_file.seek(0)

        if file_name.endswith(".pdf"):
            pdf_bytes = uploaded_file.read()

            if not pdf_bytes.startswith(b"%PDF-"):
                raise ValueError(
                    "The uploaded file is not a valid PDF. "
                    "Please upload a proper PDF resume."
                )

            reader = PdfReader(io.BytesIO(pdf_bytes), strict=False)

            if reader.is_encrypted:
                raise ValueError(
                    "This PDF is password-protected. "
                    "Please upload an unlocked PDF."
                )

            text = ""

            for page in reader.pages:
                text += (page.extract_text() or "") + "\n"

            if not text.strip():
                raise ValueError(
                    "No readable text found. "
                    "Please upload a text-based PDF resume."
                )

            return text.strip()

        elif file_name.endswith(".docx"):
            document = Document(uploaded_file)

            text = "\n".join(
                paragraph.text
                for paragraph in document.paragraphs
            )

            if not text.strip():
                raise ValueError(
                    "No readable text found in the DOCX file."
                )

            return text.strip()

        else:
            raise ValueError(
                "Unsupported file format. Upload a PDF or DOCX file."
            )

    except errors.PdfReadError as e:
        raise ValueError(
            "Unable to read this PDF. The file may be corrupted "
            "or incomplete. Please open the resume and save it "
            "again as a new PDF."
        ) from e

    finally:
        uploaded_file.seek(0)
