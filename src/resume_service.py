import base64
import json
import sys
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List

from .infrai_pdf_client import PdfParseClient


@dataclass
class ResumeRequest:
    pdf_path: str


@dataclass
class ReviewRecord:
    candidate: Dict[str, Any]
    employment: List[Dict[str, Any]]
    payment_events: List[Dict[str, Any]]
    notification: str
    action: str


def decide(parsed: Dict[str, Any]) -> ReviewRecord:
    candidate = parsed.get("candidate") or {}
    employment = parsed.get("employment") or []
    events = parsed.get("payment_events") or []
    needs_review = not candidate.get("name") or not employment
    unresolved = [e for e in events if e.get("status") in {"disputed", "unresolved"}]
    if unresolved:
        needs_review = True
    notification = "manual review required: payment event needs evidence" if unresolved else "automated checks passed"
    return ReviewRecord(candidate, employment, events, notification, "manual_review" if needs_review else "advance")


def parse_resume(request: ResumeRequest, client: PdfParseClient | None = None) -> ReviewRecord:
    with open(request.pdf_path, "rb") as handle:
        encoded = base64.b64encode(handle.read()).decode("ascii")
    parsed = (client or PdfParseClient()).parse(encoded)
    return decide(parsed)


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: python3 -m src.resume_service PDF_PATH")
    print(json.dumps(asdict(parse_resume(ResumeRequest(sys.argv[1]))), indent=2))


if __name__ == "__main__":
    main()
