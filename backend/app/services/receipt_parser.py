import io
import logging
import re
from datetime import datetime
from decimal import Decimal

logger = logging.getLogger(__name__)


class ReceiptParser:
    """Parse receipts from PDF, image (OCR stub), or plain text.

    For PDFs: uses pdfplumber to extract text, then regex-pulls amount + date + description.
    For plain text: direct regex extraction.
    For images: returns raw_data flagged for manual review (OCR not yet wired).
    """

    async def parse(self, raw: bytes, filename: str, content_type: str) -> dict:
        ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
        result = {"amount": Decimal("0"), "description": "", "transaction_date": datetime.utcnow(), "raw_data": {}}

        if content_type == "application/pdf" or ext == "pdf":
            text = self._extract_pdf_text(raw)
        elif content_type.startswith("text/") or ext in ("txt", "csv"):
            text = raw.decode("utf-8", errors="replace")
        elif content_type.startswith("image/") or ext in ("png", "jpg", "jpeg", "webp"):
            text = ""
            result["raw_data"] = {"note": "OCR not implemented; manual review required"}
        else:
            text = raw.decode("utf-8", errors="replace")

        if text:
            result["amount"] = self._extract_amount(text)
            result["description"] = self._extract_description(text, filename)
            parsed_date = self._extract_date(text)
            result["transaction_date"] = parsed_date or datetime.utcnow()
            result["raw_data"]["parsed_text"] = text[:2000]

        logger.info("Parsed receipt: amount=%s desc='%s'", result["amount"], result["description"])
        return result

    def _extract_pdf_text(self, raw: bytes) -> str:
        try:
            import pdfplumber
            text = ""
            with pdfplumber.open(io.BytesIO(raw)) as pdf:
                for page in pdf.pages:
                    text += (page.extract_text() or "") + "\n"
            return text.strip()
        except Exception as e:
            logger.warning("pdfplumber failed: %s", e)
            return ""

    def _extract_amount(self, text: str) -> Decimal:
        patterns = [
            r"(?:total|importe|monto|amount|total a pagar)[:\s]*\$?\s*([\d,]+\.\d{2})",
            r"\$?\s*([\d,]+\.\d{2})\s*(?:total|importe|monto)",
            r"(?:total)[:\s]*\$?\s*([\d,]+(?:\.\d{1,2})?)",
        ]
        for pat in patterns:
            match = re.search(pat, text, re.IGNORECASE)
            if match:
                raw = match.group(1).replace(",", "")
                try:
                    return Decimal(raw)
                except Exception:
                    continue
        return Decimal("0")

    def _extract_date(self, text: str) -> datetime | None:
        patterns = [
            r"(\d{2}/\d{2}/\d{4})",
            r"(\d{4}-\d{2}-\d{2})",
            r"(\d{2}\.\d{2}\.\d{4})",
        ]
        for pat in patterns:
            match = re.search(pat, text)
            if match:
                try:
                    for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d.%m.%Y"):
                        try:
                            return datetime.strptime(match.group(1), fmt)
                        except ValueError:
                            continue
                except Exception:
                    continue
        return None

    def _extract_description(self, text: str, filename: str) -> str:
        lines = [l.strip() for l in text.split("\n") if l.strip()]
        # First non-empty line that looks like a merchant name
        merchant = ""
        for l in lines[:5]:
            if len(l) > 3 and not any(k in l.lower() for k in ("total", "importe", "cuit", "fecha", "recibo")):
                merchant = l
                break
        return merchant or f"Receipt: {filename}"
