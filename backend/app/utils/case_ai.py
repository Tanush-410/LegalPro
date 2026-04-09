"""
Lightweight AI-style utilities for case summarization and similarity ranking.
"""
from __future__ import annotations

import re
from collections import Counter
from datetime import datetime
from typing import Dict, List, Optional, Sequence, Tuple

from app.models import Case, Judgment


STOP_WORDS = {
    "the", "and", "for", "that", "with", "this", "from", "were", "have", "has",
    "had", "not", "all", "any", "are", "was", "but", "its", "their", "his",
    "her", "they", "been", "into", "over", "under", "shall", "also", "court",
    "case", "petition", "judgment", "order", "appellant", "respondent", "india",
    "high", "supreme", "section", "article", "act", "law", "para", "held",
}


def _latest_judgment(case: Case) -> Optional[Judgment]:
    judgments = list(getattr(case, "judgments", []) or [])
    if not judgments:
        return None
    return max(judgments, key=lambda j: (j.judgment_date or j.created_at, j.created_at))


def _tokenize(text: str) -> List[str]:
    tokens = re.findall(r"\b[a-zA-Z0-9]{3,}\b", (text or "").lower())
    return [t for t in tokens if t not in STOP_WORDS]


def _split_sentences(text: str) -> List[str]:
    raw = re.split(r"(?<=[.!?])\s+", (text or "").strip())
    return [s.strip() for s in raw if s and len(s.strip()) > 20]


def _extractive_summary(text: str, max_sentences: int = 3, max_chars: int = 900) -> str:
    sentences = _split_sentences(text)
    if not sentences:
        return ""

    token_counts = Counter(_tokenize(text))
    if not token_counts:
        return " ".join(sentences[:max_sentences])[:max_chars].strip()

    scored: List[Tuple[int, float]] = []
    for idx, sent in enumerate(sentences):
        stokens = _tokenize(sent)
        if not stokens:
            continue
        score = sum(token_counts.get(tok, 0) for tok in stokens) / max(len(stokens), 1)
        scored.append((idx, score))

    if not scored:
        return " ".join(sentences[:max_sentences])[:max_chars].strip()

    top_indices = sorted([idx for idx, _ in sorted(scored, key=lambda x: x[1], reverse=True)[:max_sentences]])
    picked = [sentences[idx] for idx in top_indices]
    summary = " ".join(picked).strip()
    return summary[:max_chars].strip()


def _build_case_text(case: Case, judgment: Optional[Judgment]) -> str:
    parts = [
        case.case_number or "",
        case.case_type or "",
        case.petitioner or "",
        case.respondent or "",
        getattr(case.court, "name", "") if getattr(case, "court", None) else "",
    ]
    if judgment:
        parts.extend([
            judgment.judge_name or "",
            judgment.verdict or "",
            judgment.judgment_text or "",
        ])
    return " ".join(parts).strip()


def summarize_case(case: Case) -> Dict[str, str]:
    judgment = _latest_judgment(case)
    body_text = ""
    if judgment:
        body_text = " ".join([
            judgment.verdict or "",
            judgment.judgment_text or "",
        ]).strip()

    summary = _extractive_summary(body_text)
    if not summary:
        summary = (
            f"{case.case_type or 'Case'} in {getattr(case.court, 'name', 'court')}. "
            f"Petitioner: {case.petitioner or 'N/A'}. Respondent: {case.respondent or 'N/A'}. "
            f"Judge: {(judgment.judge_name if judgment else None) or 'N/A'}."
        )

    return {
        "summary": summary,
        "method": "extractive-local",
    }


def _score_similarity(
    target_case: Case,
    target_judgment: Optional[Judgment],
    candidate_case: Case,
    candidate_judgment: Optional[Judgment],
) -> Tuple[float, List[str]]:
    target_text = _build_case_text(target_case, target_judgment)
    candidate_text = _build_case_text(candidate_case, candidate_judgment)
    tset = set(_tokenize(target_text))
    cset = set(_tokenize(candidate_text))

    if tset and cset:
        overlap = tset.intersection(cset)
        jaccard = len(overlap) / len(tset.union(cset))
    else:
        overlap = set()
        jaccard = 0.0

    bonus = 0.0
    if getattr(target_case.court, "level", None) == getattr(candidate_case.court, "level", None):
        bonus += 0.12
    if (target_case.case_type or "").lower() == (candidate_case.case_type or "").lower():
        bonus += 0.10
    if getattr(target_case.court, "name", "") == getattr(candidate_case.court, "name", ""):
        bonus += 0.06
    if target_judgment and candidate_judgment and target_judgment.judge_name and candidate_judgment.judge_name:
        if target_judgment.judge_name == candidate_judgment.judge_name:
            bonus += 0.05

    score = jaccard + bonus
    top_terms = sorted(list(overlap), key=len, reverse=True)[:6]
    return score, top_terms


def find_similar_cases(target_case: Case, all_cases: Sequence[Case], limit: int = 5) -> List[Dict]:
    target_judgment = _latest_judgment(target_case)
    scored: List[Tuple[float, Case, Optional[Judgment], List[str]]] = []

    for candidate in all_cases:
        if candidate.id == target_case.id:
            continue
        cjudgment = _latest_judgment(candidate)
        score, overlap_terms = _score_similarity(target_case, target_judgment, candidate, cjudgment)
        if score <= 0:
            continue
        scored.append((score, candidate, cjudgment, overlap_terms))

    scored.sort(key=lambda item: (item[0], item[1].case_date or datetime.min), reverse=True)
    results = []
    for score, c, cjudgment, terms in scored[: max(1, min(limit, 20))]:
        results.append(
            {
                "id": c.id,
                "case_number": c.case_number,
                "case_type": c.case_type,
                "court_name": c.court.name if c.court else None,
                "court_level": c.court.level.value if c.court and c.court.level else None,
                "judge_name": cjudgment.judge_name if cjudgment else None,
                "case_date": c.case_date.isoformat() if c.case_date else None,
                "score": round(score, 4),
                "overlap_terms": terms,
            }
        )
    return results
