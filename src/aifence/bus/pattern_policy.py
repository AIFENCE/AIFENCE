# SPDX-License-Identifier: AGPL-3.0-or-later
# SAGE is dual-licensed under AGPL-3.0-or-later and a commercial license.
# Contact sage@digitalacre.org for commercial licensing.
from __future__ import annotations

import math

from .config import Settings
from .db_models import LearnedPattern


def trust_ready(settings: Settings, diversity: int, dominant_share: float, trust_score: float, scope: str) -> bool:
    if not settings.pattern_trust_required:
        return True
    scope_minimums = {
        "session": settings.pattern_session_min_sources,
        "project": settings.pattern_project_min_sources,
        "workspace": settings.pattern_workspace_min_sources,
        "domain": settings.pattern_domain_min_sources,
        "federation": settings.pattern_federation_min_sources,
    }
    minimum_sources = max(settings.pattern_min_source_diversity, scope_minimums.get(scope, scope_minimums["session"]))
    return diversity >= minimum_sources and dominant_share <= settings.pattern_max_source_share and trust_score >= settings.pattern_min_trust_score


def utility_score(pattern: LearnedPattern) -> float:
    task = pattern.task_utility if pattern.task_utility is not None else 0.5
    stability = max(0.0, 1.0 - pattern.semantic_variance)
    frequency = math.log1p(max(0, pattern.occurrence_count))
    savings = max(0.0, pattern.estimated_savings_bytes / 64.0)
    score = frequency * savings * max(0.05, task) * stability * max(0.05, pattern.interoperability_score)
    return score / (1.0 + max(0.0, pattern.ambiguity_score))
