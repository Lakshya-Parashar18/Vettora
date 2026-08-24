import json
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

from app.main import app
from app.services.resume_parser import (
    extract_email,
    extract_phone,
    normalize_text,
    parse_resume_file,
    ResumeParsingError,
)

client = TestClient(app)

SAMPLE_LLM_RESPONSE = {
    "candidate": {"name": "Jane Doe", "email": "jane.doe@techcorp.io", "phone": "+91 91234 56789"},
    "skills": ["Python", "FastAPI"],
    "education": [],
    "experience": [],
    "projects": [],
    "certifications": [],
}


def _mock_llm(data: dict):
    mock_response = MagicMock()
    mock_response.text = json.dumps(data)
    return mock_response


def test_deterministic_email_extraction():
    text = "Candidate Name\nContact: john.doe@example.com\nPhone: +91 98765 43210"
    assert extract_email(text) == "john.doe@example.com"


def test_deterministic_phone_extraction():
    sample1 = "Contact me at +91 98765 43210 for inquiries."
    sample2 = "Mobile: 9876543210"
    sample3 = "Phone: +91-98765-43210"

    assert extract_phone(sample1) is not None
    assert extract_phone(sample2) is not None
    assert extract_phone(sample3) is not None


def test_text_normalization():
    raw = "Line 1\r\n\r\n\r\nLine 2   \n\n\nLine 3"
    normalized = normalize_text(raw)
    assert "\r" not in normalized
    assert "Line 1\n\nLine 2\n\nLine 3" == normalized


@patch("app.services.llm_service._get_client")
def test_txt_resume_parsing(mock_get_client):
    mock_client = MagicMock()
    mock_client.models.generate_content.return_value = _mock_llm(SAMPLE_LLM_RESPONSE)
    mock_get_client.return_value = mock_client

    content = b"Jane Doe\nEmail: jane.doe@techcorp.io\nPhone: +91 91234 56789\nExperience: Senior Engineer with 6 years experience."
    res = parse_resume_file("jane_resume.txt", content)

    assert res.status == "processed"
    assert res.extraction_method == "native"
    assert res.candidate.email == "jane.doe@techcorp.io"
    assert res.candidate.name == "Jane Doe"
    assert res.candidate.phone is not None
    assert "Senior Engineer" in res.normalized_text
    assert res.resume is not None
    assert res.resume.metadata.llm_structured is True


def test_unsupported_file_type():
    content = b"some image content"
    res = parse_resume_file("photo.png", content)

    assert res.status == "failed"
    assert res.error.code == "unsupported_file_type"


def test_oversized_file():
    large_content = b"a" * (11 * 1024 * 1024)
    res = parse_resume_file("large_resume.txt", large_content)

    assert res.status == "failed"
    assert res.error.code == "oversized_file"


def test_empty_text_resume_handling():
    content = b"Short text"
    res = parse_resume_file("scanned.txt", content)

    assert res.status == "failed"
    assert res.error.code == "empty_resume"


@patch("app.services.llm_service._get_client")
@patch("pdfplumber.open")
def test_native_pdf_extraction_skips_ocr(mock_pdfplumber, mock_get_client):
    mock_page = MagicMock()
    mock_page.extract_text.return_value = "John Doe\nEmail: john@domain.com\nSenior Software Architect with 10 years experience."

    mock_pdf = MagicMock()
    mock_pdf.pages = [mock_page]
    mock_pdfplumber.return_value.__enter__.return_value = mock_pdf

    llm_data = {**SAMPLE_LLM_RESPONSE, "candidate": {"name": "John Doe", "email": "john@domain.com", "phone": None}}
    mock_client = MagicMock()
    mock_client.models.generate_content.return_value = _mock_llm(llm_data)
    mock_get_client.return_value = mock_client

    res = parse_resume_file("john_resume.pdf", b"%PDF-1.4 sample content")

    assert res.status == "processed"
    assert res.extraction_method == "native"
    assert res.candidate.email == "john@domain.com"
    assert mock_page.to_image.call_count == 0


@patch("app.services.llm_service._get_client")
@patch("app.services.resume_parser.is_tesseract_available", return_value=True)
@patch("pytesseract.image_to_string")
@patch("pdfplumber.open")
def test_scanned_pdf_ocr_fallback(mock_pdfplumber, mock_ocr, mock_tesseract_avail, mock_get_client):
    mock_page = MagicMock()
    mock_page.extract_text.return_value = ""
    mock_page.to_image.return_value.original = MagicMock()

    mock_pdf = MagicMock()
    mock_pdf.pages = [mock_page]
    mock_pdfplumber.return_value.__enter__.return_value = mock_pdf

    mock_ocr.return_value = "Sarah Connor\nEmail: sarah@skynet.com\nPhone: +91 99999 88888\nCyberdyne Systems Lead Engineer."

    llm_data = {**SAMPLE_LLM_RESPONSE, "candidate": {"name": "Sarah Connor", "email": "sarah@skynet.com", "phone": "+91 99999 88888"}}
    mock_client = MagicMock()
    mock_client.models.generate_content.return_value = _mock_llm(llm_data)
    mock_get_client.return_value = mock_client

    res = parse_resume_file("scanned_resume.pdf", b"%PDF-1.4 sample content")

    assert res.status == "processed"
    assert res.extraction_method == "ocr"
    assert res.candidate.email == "sarah@skynet.com"
    assert mock_ocr.call_count == 1


@patch("app.services.llm_service._get_client")
@patch("app.services.resume_parser.is_tesseract_available", return_value=True)
@patch("pytesseract.image_to_string")
@patch("pdfplumber.open")
def test_multipage_scanned_pdf_ocr(mock_pdfplumber, mock_ocr, mock_tesseract_avail, mock_get_client):
    mock_page1 = MagicMock()
    mock_page1.extract_text.return_value = ""
    mock_page1.to_image.return_value.original = MagicMock()

    mock_page2 = MagicMock()
    mock_page2.extract_text.return_value = ""
    mock_page2.to_image.return_value.original = MagicMock()

    mock_pdf = MagicMock()
    mock_pdf.pages = [mock_page1, mock_page2]
    mock_pdfplumber.return_value.__enter__.return_value = mock_pdf

    mock_ocr.side_effect = [
        "Page 1: Bruce Wayne\nEmail: bruce@wayne.com\nCEO & Founder at Wayne Enterprises.",
        "Page 2: Education: Master of Science in Applied Physics.\nProjects & Skills.",
    ]

    llm_data = {**SAMPLE_LLM_RESPONSE, "candidate": {"name": "Bruce Wayne", "email": "bruce@wayne.com", "phone": None}}
    mock_client = MagicMock()
    mock_client.models.generate_content.return_value = _mock_llm(llm_data)
    mock_get_client.return_value = mock_client

    res = parse_resume_file("multipage_scanned.pdf", b"%PDF-1.4 sample content")

    assert res.status == "processed"
    assert res.extraction_method == "ocr"
    assert "Wayne Enterprises" in res.normalized_text
    assert "Applied Physics" in res.normalized_text
    assert mock_ocr.call_count == 2


@patch("app.services.llm_service._get_client")
@patch("app.services.resume_parser.is_tesseract_available", return_value=True)
@patch("pytesseract.image_to_string")
@patch("pdfplumber.open")
def test_hybrid_mixed_pdf_extraction(mock_pdfplumber, mock_ocr, mock_tesseract_avail, mock_get_client):
    mock_page1 = MagicMock()
    mock_page1.extract_text.return_value = "Diana Prince\nEmail: diana@themyscira.org\nChief Curator with 8 years experience."

    mock_page2 = MagicMock()
    mock_page2.extract_text.return_value = ""
    mock_page2.to_image.return_value.original = MagicMock()

    mock_pdf = MagicMock()
    mock_pdf.pages = [mock_page1, mock_page2]
    mock_pdfplumber.return_value.__enter__.return_value = mock_pdf

    mock_ocr.return_value = "Page 2 Scanned Appendix: Publications & Research Papers in Archaeology."

    llm_data = {**SAMPLE_LLM_RESPONSE, "candidate": {"name": "Diana Prince", "email": "diana@themyscira.org", "phone": None}}
    mock_client = MagicMock()
    mock_client.models.generate_content.return_value = _mock_llm(llm_data)
    mock_get_client.return_value = mock_client

    res = parse_resume_file("mixed_resume.pdf", b"%PDF-1.4 sample content")

    assert res.status == "processed"
    assert res.extraction_method == "hybrid"
    assert "Diana Prince" in res.normalized_text
    assert "Archaeology" in res.normalized_text
    assert mock_ocr.call_count == 1


@patch("app.services.resume_parser.is_tesseract_available", return_value=False)
@patch("pdfplumber.open")
def test_ocr_unavailable_error(mock_pdfplumber, mock_tesseract_avail):
    mock_page = MagicMock()
    mock_page.extract_text.return_value = ""

    mock_pdf = MagicMock()
    mock_pdf.pages = [mock_page]
    mock_pdfplumber.return_value.__enter__.return_value = mock_pdf

    res = parse_resume_file("scanned_no_ocr.pdf", b"%PDF-1.4 sample content")

    assert res.status == "failed"
    assert res.error.code == "ocr_unavailable"


@patch("app.services.resume_parser.is_tesseract_available", return_value=True)
@patch("pytesseract.image_to_string", return_value="")
@patch("pdfplumber.open")
def test_ocr_failed_empty_result(mock_pdfplumber, mock_ocr, mock_tesseract_avail):
    mock_page = MagicMock()
    mock_page.extract_text.return_value = ""
    mock_page.to_image.return_value.original = MagicMock()

    mock_pdf = MagicMock()
    mock_pdf.pages = [mock_page]
    mock_pdfplumber.return_value.__enter__.return_value = mock_pdf

    res = parse_resume_file("blank_scanned.pdf", b"%PDF-1.4 sample content")

    assert res.status == "failed"
    assert res.error.code == "ocr_failed"


@patch("app.services.llm_service._get_client")
def test_resume_upload_endpoint(mock_get_client):
    llm_data = {
        "candidate": {"name": "Alex Smith", "email": "alex.smith@dev.com", "phone": "+91 99887 76655"},
        "skills": ["React", "FastAPI", "Python"],
        "education": [],
        "experience": [],
        "projects": [],
        "certifications": [],
    }
    mock_client = MagicMock()
    mock_client.models.generate_content.return_value = _mock_llm(llm_data)
    mock_get_client.return_value = mock_client

    txt_content = b"Alex Smith\nEmail: alex.smith@dev.com\nPhone: +91 99887 76655\nSkills: React, FastAPI, Python."

    response = client.post(
        "/resumes/upload",
        files=[("files", ("alex_resume.txt", txt_content, "text/plain"))],
    )

    assert response.status_code == 200
    data = response.json()
    assert "resumes" in data
    assert len(data["resumes"]) == 1

    item = data["resumes"][0]
    assert item["filename"] == "alex_resume.txt"
    assert item["status"] == "processed"
    assert item["extraction_method"] == "native"
    assert item["candidate"]["email"] == "alex.smith@dev.com"
    assert item["resume"]["metadata"]["llm_structured"] is True
    assert "Python" in item["resume"]["skills"]
