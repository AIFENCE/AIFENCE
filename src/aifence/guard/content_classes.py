# SPDX-License-Identifier: AGPL-3.0-or-later
"""Derive data classes from actual content, rather than trusting declaration.

``SecurityContext.data_classes`` is supplied by the caller, so enforcement that
relies on it alone is only as honest as the agent. This module inspects the
content itself and reports which sensitive classes are *observed*, letting the
existing data-class machinery (exfiltration and secret-exposure rules) act on
what is really there.

Two deliberate constraints:

* **Precision over recall.** Observed classes feed rules whose baseline outcome
  is ``deny``, so every pattern requires a strong signal — card numbers must pass
  a Luhn check, national IDs exclude structurally invalid ranges, and generic
  secrets need an assignment context rather than looking like random text.
* **Never echo the match.** Only class names and counts are returned. Matched
  values are the sensitive data; they must not reach findings, logs, or receipts.
"""
from __future__ import annotations

import re
from collections import Counter
from collections.abc import Iterable

#: Classes that the baseline policy already treats as sensitive.
GOVERNMENT_ID = "government_id"
FINANCIAL = "financial"
CREDENTIAL = "credential"
SECRET = "secret"
HEALTH = "health"
#: Informational: personally identifying but not in the baseline sensitive set.
PERSONAL_DATA = "personal_data"

_EMAIL = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
# E.164 and common grouped forms; requires a separator or country code so bare
# integers do not match.
_PHONE = re.compile(r"(?<!\d)(?:\+\d{1,3}[ .-]?)?(?:\(\d{3}\)|\d{3})[ .-]\d{3}[ .-]\d{4}(?!\d)")
_US_SSN = re.compile(r"(?<!\d)(\d{3})-(\d{2})-(\d{4})(?!\d)")
_CARD = re.compile(r"(?<!\d)(?:\d[ -]?){13,19}(?!\d)")
_IBAN = re.compile(r"\b[A-Z]{2}\d{2}[A-Z0-9]{11,30}\b")
_AWS_KEY = re.compile(r"\b(?:AKIA|ASIA|AGPA|AIDA|AROA|ANPA|ANVA)[A-Z0-9]{16}\b")
_PRIVATE_KEY = re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |PGP )?PRIVATE KEY-----")
_JWT = re.compile(r"\beyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\b")
_SLACK_TOKEN = re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b")
_GITHUB_TOKEN = re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{36}\b")
# A secret only counts when it is *assigned* to a secret-ish name, so ordinary
# prose containing a long token does not trip the deny path.
_ASSIGNED_SECRET = re.compile(
    r"(?i)\b(?:api[_-]?key|secret|token|passwd|password|client[_-]?secret|private[_-]?key)\b"
    r"\s*[:=]\s*[\"']?([A-Za-z0-9/+_\-]{16,})[\"']?"
)
_HEALTH_TERMS = re.compile(
    r"(?i)\b(?:diagnos(?:is|ed)|prognosis|prescription|prescribed|icd-?10|"
    r"medical record|patient id|blood type|hiv status)\b"
)


def _luhn_ok(digits: str) -> bool:
    total = 0
    for index, char in enumerate(reversed(digits)):
        value = int(char)
        if index % 2 == 1:
            value *= 2
            if value > 9:
                value -= 9
        total += value
    return total % 10 == 0


def _valid_us_ssn(area: str, group: str, serial: str) -> bool:
    if area in {"000", "666"} or area.startswith("9"):
        return False
    return group != "00" and serial != "0000"


def _count_cards(text: str) -> int:
    found = 0
    for match in _CARD.finditer(text):
        digits = re.sub(r"[ -]", "", match.group(0))
        if 13 <= len(digits) <= 19 and _luhn_ok(digits):
            found += 1
    return found


def classify(text: str) -> dict[str, int]:
    """Return observed sensitive classes mapped to match counts.

    Never returns the matched values themselves.
    """
    if not text:
        return {}
    counts: Counter[str] = Counter()

    ssn_hits = sum(1 for m in _US_SSN.finditer(text) if _valid_us_ssn(*m.groups()))
    if ssn_hits:
        counts[GOVERNMENT_ID] += ssn_hits

    cards = _count_cards(text)
    ibans = len(_IBAN.findall(text))
    if cards or ibans:
        counts[FINANCIAL] += cards + ibans

    credential_hits = (
        len(_AWS_KEY.findall(text))
        + len(_JWT.findall(text))
        + len(_SLACK_TOKEN.findall(text))
        + len(_GITHUB_TOKEN.findall(text))
        + len(_ASSIGNED_SECRET.findall(text))
    )
    if credential_hits:
        counts[CREDENTIAL] += credential_hits

    key_blocks = len(_PRIVATE_KEY.findall(text))
    if key_blocks:
        counts[SECRET] += key_blocks

    if _HEALTH_TERMS.search(text):
        counts[HEALTH] += len(_HEALTH_TERMS.findall(text))

    personal = len(_EMAIL.findall(text)) + len(_PHONE.findall(text))
    if personal:
        counts[PERSONAL_DATA] += personal

    return dict(counts)


def classify_all(values: Iterable[str]) -> dict[str, int]:
    """Classify several strings, summing the per-class counts."""
    totals: Counter[str] = Counter()
    for value in values:
        totals.update(classify(value))
    return dict(totals)
