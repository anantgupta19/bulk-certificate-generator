from pathlib import Path
import re

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas


OUTPUT_DIR = Path("generated_certificates")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# Color palette
NAVY = colors.HexColor("#17365D")
DARK_NAVY = colors.HexColor("#102A43")
GOLD = colors.HexColor("#C9A227")
LIGHT_GOLD = colors.HexColor("#E8D48A")
TEXT = colors.HexColor("#333333")
MUTED = colors.HexColor("#666666")
WHITE = colors.white


def _safe_filename(value: str) -> str:
    """Convert a recipient name into a safe filename."""
    value = re.sub(r"[^a-zA-Z0-9_-]+", "_", value)
    return value.strip("_") or "recipient"


def _draw_corner_ornament(pdf, x, y, size=35):
    """Draw a small decorative corner element."""
    pdf.setStrokeColor(GOLD)
    pdf.setLineWidth(1.5)

    pdf.line(x, y, x + size, y)
    pdf.line(x, y, x, y + size)

    pdf.setLineWidth(0.8)
    pdf.line(x + 7, y + 7, x + size - 5, y + 7)
    pdf.line(x + 7, y + 7, x + 7, y + size - 5)


def _draw_seal(pdf, x, y):
    """Draw a simple certificate seal."""
    pdf.setStrokeColor(GOLD)
    pdf.setFillColor(colors.HexColor("#FFF8DC"))

    pdf.setLineWidth(2)
    pdf.circle(x, y, 27, fill=1, stroke=1)

    pdf.setLineWidth(1)
    pdf.circle(x, y, 21, fill=0, stroke=1)

    pdf.setFillColor(NAVY)
    pdf.setFont("Helvetica-Bold", 8)
    pdf.drawCentredString(x, y + 4, "CERTIFIED")

    pdf.setFont("Helvetica", 6)
    pdf.drawCentredString(x, y - 7, "2026")


def generate_certificate(
    recipient_name: str,
    organization: str,
    event_name: str,
    event_date: str,
    certificate_type: str,
    certificate_id: int,
) -> str:
    """
    Generate an aesthetically formatted certificate PDF.
    """

    filename = (
        f"{certificate_id}_"
        f"{_safe_filename(recipient_name)}.pdf"
    )

    file_path = OUTPUT_DIR / filename

    page_width, page_height = landscape(A4)

    pdf = canvas.Canvas(
        str(file_path),
        pagesize=(page_width, page_height)
    )

    # ---------------------------------------------------------
    # Background
    # ---------------------------------------------------------

    pdf.setFillColor(WHITE)
    pdf.rect(
        0,
        0,
        page_width,
        page_height,
        fill=1,
        stroke=0
    )

    # Very subtle inner background
    pdf.setFillColor(colors.HexColor("#FCFBF7"))
    pdf.rect(
        48,
        48,
        page_width - 96,
        page_height - 96,
        fill=1,
        stroke=0
    )

    # ---------------------------------------------------------
    # Outer borders
    # ---------------------------------------------------------

    pdf.setStrokeColor(DARK_NAVY)
    pdf.setLineWidth(5)

    pdf.rect(
        22,
        22,
        page_width - 44,
        page_height - 44,
        fill=0,
        stroke=1
    )

    pdf.setStrokeColor(GOLD)
    pdf.setLineWidth(1.8)

    pdf.rect(
        34,
        34,
        page_width - 68,
        page_height - 68,
        fill=0,
        stroke=1
    )

    pdf.setStrokeColor(LIGHT_GOLD)
    pdf.setLineWidth(0.8)

    pdf.rect(
        42,
        42,
        page_width - 84,
        page_height - 84,
        fill=0,
        stroke=1
    )

    # Corner decorations
    _draw_corner_ornament(pdf, 48, 48)
    _draw_corner_ornament(pdf, 48, page_height - 48, 35)
    _draw_corner_ornament(
        pdf,
        page_width - 48,
        48,
        35
    )

    # Top-right ornament
    pdf.saveState()
    pdf.translate(page_width - 48, page_height - 48)
    pdf.rotate(90)
    _draw_corner_ornament(pdf, 0, 0)
    pdf.restoreState()

    # ---------------------------------------------------------
    # Organization
    # ---------------------------------------------------------

    pdf.setFillColor(NAVY)
    pdf.setFont("Helvetica-Bold", 19)

    pdf.drawCentredString(
        page_width / 2,
        page_height - 78,
        organization.upper()
    )

    # Decorative divider
    center_x = page_width / 2

    pdf.setStrokeColor(GOLD)
    pdf.setLineWidth(1.5)

    pdf.line(
        center_x - 150,
        page_height - 95,
        center_x - 25,
        page_height - 95
    )

    pdf.line(
        center_x + 25,
        page_height - 95,
        center_x + 150,
        page_height - 95
    )

    pdf.setFillColor(GOLD)
    pdf.circle(
        center_x,
        page_height - 95,
        3,
        fill=1,
        stroke=0
    )

    # ---------------------------------------------------------
    # Main title
    # ---------------------------------------------------------

    pdf.setFillColor(DARK_NAVY)
    pdf.setFont("Helvetica-Bold", 34)

    pdf.drawCentredString(
        center_x,
        page_height - 145,
        "CERTIFICATE"
    )

    pdf.setFillColor(GOLD)
    pdf.setFont("Helvetica-Bold", 15)

    pdf.drawCentredString(
        center_x,
        page_height - 172,
        f"OF {certificate_type.upper()}"
    )

    # ---------------------------------------------------------
    # Introductory text
    # ---------------------------------------------------------

    pdf.setFillColor(TEXT)
    pdf.setFont("Helvetica", 12)

    pdf.drawCentredString(
        center_x,
        page_height - 215,
        "This certificate is proudly presented to"
    )

    # ---------------------------------------------------------
    # Recipient
    # ---------------------------------------------------------

    pdf.setFillColor(NAVY)
    pdf.setFont("Helvetica-Bold", 30)

    pdf.drawCentredString(
        center_x,
        page_height - 260,
        recipient_name
    )

    # Name underline
    pdf.setStrokeColor(GOLD)
    pdf.setLineWidth(2)

    pdf.line(
        center_x - 180,
        page_height - 274,
        center_x + 180,
        page_height - 274
    )

    # ---------------------------------------------------------
    # Event information
    # ---------------------------------------------------------

    pdf.setFillColor(TEXT)
    pdf.setFont("Helvetica", 12)

    pdf.drawCentredString(
        center_x,
        page_height - 310,
        f"for {certificate_type.lower()} in"
    )

    pdf.setFillColor(DARK_NAVY)
    pdf.setFont("Helvetica-Bold", 16)

    pdf.drawCentredString(
        center_x,
        page_height - 337,
        event_name
    )

    pdf.setFillColor(MUTED)
    pdf.setFont("Helvetica", 10)

    pdf.drawCentredString(
        center_x,
        page_height - 362,
        f"Date of Event: {event_date}"
    )

    # ---------------------------------------------------------
    # Signature section
    # ---------------------------------------------------------

    signature_y = 82

    # Left signature
    pdf.setStrokeColor(colors.HexColor("#777777"))
    pdf.setLineWidth(0.8)

    pdf.line(
        105,
        signature_y + 18,
        245,
        signature_y + 18
    )

    pdf.setFillColor(TEXT)
    pdf.setFont("Helvetica-Bold", 9)

    pdf.drawCentredString(
        175,
        signature_y + 5,
        "Authorized Signatory"
    )

    # Right signature
    pdf.line(
        page_width - 245,
        signature_y + 18,
        page_width - 105,
        signature_y + 18
    )

    pdf.drawCentredString(
        page_width - 175,
        signature_y + 5,
        "Program Coordinator"
    )

    # ---------------------------------------------------------
    # Seal
    # ---------------------------------------------------------

    _draw_seal(
        pdf,
        center_x,
        signature_y + 18
    )

    # ---------------------------------------------------------
    # Footer
    # ---------------------------------------------------------

    pdf.setFillColor(MUTED)
    pdf.setFont("Helvetica", 7.5)

    pdf.drawString(
        55,
        48,
        f"Certificate ID: {certificate_id}"
    )

    pdf.drawRightString(
        page_width - 55,
        48,
        "Bulk Certificate Generator API"
    )

    pdf.save()

    return str(file_path)