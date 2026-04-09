"""
Minimal PDF report builder without external dependencies.
"""
from __future__ import annotations

from datetime import datetime
from textwrap import wrap
from typing import Iterable, List, Sequence


def _fmt_dt(value) -> str:
    if value is None:
        return "N/A"
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d %H:%M:%S UTC")
    return str(value)


def _escape_pdf_text(value: str) -> str:
    return value.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _paginate_lines(lines: Sequence[str], max_chars: int = 100, max_lines_per_page: int = 46) -> List[List[str]]:
    expanded: List[str] = []
    for line in lines:
        if not line:
            expanded.append("")
            continue
        wrapped = wrap(line, width=max_chars, break_long_words=False, break_on_hyphens=False)
        expanded.extend(wrapped or [""])

    pages: List[List[str]] = []
    for idx in range(0, len(expanded), max_lines_per_page):
        pages.append(expanded[idx : idx + max_lines_per_page])
    return pages or [["No content available"]]


def _build_pdf_from_lines(lines: Sequence[str]) -> bytes:
    pages = _paginate_lines(lines)

    objects: List[bytes] = []

    # 1: Catalog
    objects.append(b"<< /Type /Catalog /Pages 2 0 R >>")

    # 2: Pages object (kids filled later)
    # placeholder, replaced once page objects are known
    objects.append(b"")

    page_object_ids: List[int] = []
    for page_lines in pages:
        content_stream_lines = ["BT", "/F1 11 Tf", "50 760 Td", "14 TL"]
        first_line = True
        for line in page_lines:
            escaped = _escape_pdf_text(line)
            if first_line:
                content_stream_lines.append(f"({escaped}) Tj")
                first_line = False
            else:
                content_stream_lines.append(f"T* ({escaped}) Tj")
        content_stream_lines.append("ET")
        stream = "\n".join(content_stream_lines).encode("latin-1", errors="replace")

        content_obj_id = len(objects) + 1
        objects.append(
            b"<< /Length " + str(len(stream)).encode("ascii") + b" >>\nstream\n" + stream + b"\nendstream"
        )

        page_obj_id = len(objects) + 1
        page_object_ids.append(page_obj_id)
        objects.append(
            (
                f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
                f"/Resources << /Font << /F1 FONT_OBJ_ID 0 R >> >> "
                f"/Contents {content_obj_id} 0 R >>"
            ).encode("ascii")
        )

    # Font object (single shared Helvetica)
    font_obj_id = len(objects) + 1
    objects.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")

    # Patch all page objects to point to the final font object id
    for page_obj_id in page_object_ids:
        obj = objects[page_obj_id - 1].decode("ascii")
        obj = obj.replace("/F1 FONT_OBJ_ID 0 R", f"/F1 {font_obj_id} 0 R")
        objects[page_obj_id - 1] = obj.encode("ascii")

    # Fill pages object now
    kids = " ".join([f"{pid} 0 R" for pid in page_object_ids])
    objects[1] = f"<< /Type /Pages /Count {len(page_object_ids)} /Kids [{kids}] >>".encode("ascii")

    out = bytearray()
    out.extend(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")

    offsets = [0]
    for obj_id, payload in enumerate(objects, start=1):
        offsets.append(len(out))
        out.extend(f"{obj_id} 0 obj\n".encode("ascii"))
        out.extend(payload)
        out.extend(b"\nendobj\n")

    xref_offset = len(out)
    out.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    out.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        out.extend(f"{offset:010d} 00000 n \n".encode("ascii"))

    out.extend(
        (
            f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
            f"startxref\n{xref_offset}\n%%EOF\n"
        ).encode("ascii")
    )
    return bytes(out)


def build_case_report_pdf(case, judgments: Iterable, documents: Iterable) -> bytes:
    court_name = case.court.name if getattr(case, "court", None) else "N/A"
    court_level = case.court.level.value if getattr(case, "court", None) and getattr(case.court, "level", None) else "N/A"

    lines: List[str] = [
        "Court Ecosystem - Full Case Report",
        "",
        "Case Details",
        f"Case ID: {case.id}",
        f"Case Number: {case.case_number or 'N/A'}",
        f"Case Type: {case.case_type or 'N/A'}",
        f"Court: {court_name}",
        f"Court Level: {court_level}",
        f"Petitioner: {case.petitioner or 'N/A'}",
        f"Respondent: {case.respondent or 'N/A'}",
        f"Case Date: {_fmt_dt(case.case_date)}",
        f"Record Created At: {_fmt_dt(case.created_at)}",
        "",
        "Case Description",
        getattr(case, 'case_description', None) or "No case description available.",
        "",
        "Judgments",
    ]

    judgment_list = list(judgments)
    if not judgment_list:
        lines.append("No judgment rows available.")
    else:
        for idx, j in enumerate(judgment_list, start=1):
            lines.extend(
                [
                    f"Judgment #{idx}",
                    f"Judge Name: {getattr(j, 'judge_name', None) or 'N/A'}",
                    f"Judgment Date: {_fmt_dt(getattr(j, 'judgment_date', None))}",
                    f"Verdict: {getattr(j, 'verdict', None) or 'N/A'}",
                    "Judgment Text:",
                    getattr(j, "judgment_text", None) or "N/A",
                    "",
                ]
            )

    lines.append("Documents")
    document_list = list(documents)
    if not document_list:
        lines.append("No document rows available.")
    else:
        for idx, d in enumerate(document_list, start=1):
            lines.extend(
                [
                    f"Document #{idx}",
                    f"File Name: {getattr(d, 'file_name', None) or 'N/A'}",
                    f"File Type: {getattr(d, 'file_type', None) or 'N/A'}",
                    f"Source URL: {getattr(d, 'source_url', None) or 'N/A'}",
                    f"Stored Path: {getattr(d, 'file_path', None) or 'N/A'}",
                    "",
                ]
            )

    lines.extend(
        [
            "Provenance",
            f"Generated At: {_fmt_dt(datetime.utcnow())}",
            "Generated By: Court Ecosystem API",
        ]
    )

    return _build_pdf_from_lines(lines)
