# SPDX-License-Identifier: AGPL-3.0-or-later
# SAGE is dual-licensed under AGPL-3.0-or-later and a commercial license.
# Contact sage@digitalacre.org for commercial licensing.
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from .db_models import CalibrationBucket


@dataclass(frozen=True)
class CalibrationReport:
    sample_count: int
    expected_calibration_error: float
    brier_score: float
    calibrated_probability: float


class CalibrationStore:
    def __init__(self, db: Session, buckets: int = 10, min_samples: int = 20) -> None:
        if buckets < 2:
            raise ValueError("buckets must be >= 2")
        if min_samples < 1:
            raise ValueError("min_samples must be >= 1")
        self.db = db
        self.buckets = buckets
        self.min_samples = min_samples

    def _bucket(self, predicted: float) -> int:
        value = max(0.0, min(1.0, float(predicted)))
        return min(self.buckets - 1, int(value * self.buckets))

    def record(
        self,
        *,
        predicted: float,
        observed: float,
        workspace: str = "default",
        receiver: str = "*",
        model: str = "*",
        task_family: str = "*",
    ) -> CalibrationBucket:
        predicted = max(0.0, min(1.0, float(predicted)))
        observed = max(0.0, min(1.0, float(observed)))
        bucket = self._bucket(predicted)
        item = self.db.scalar(
            select(CalibrationBucket).where(
                CalibrationBucket.workspace == workspace,
                CalibrationBucket.receiver == receiver,
                CalibrationBucket.model == model,
                CalibrationBucket.task_family == task_family,
                CalibrationBucket.bucket == bucket,
            )
        )
        if item is None:
            item = CalibrationBucket(
                workspace=workspace,
                receiver=receiver,
                model=model,
                task_family=task_family,
                bucket=bucket,
            )
            self.db.add(item)
            self.db.flush()
        item.sample_count += 1
        item.predicted_sum += predicted
        item.observed_sum += observed
        item.squared_error_sum += (predicted - observed) ** 2
        self.db.flush()
        return item

    def rows(
        self,
        *,
        workspace: str = "default",
        receiver: str = "*",
        model: str = "*",
        task_family: str = "*",
    ) -> list[CalibrationBucket]:
        return list(
            self.db.scalars(
                select(CalibrationBucket)
                .where(
                    CalibrationBucket.workspace == workspace,
                    CalibrationBucket.receiver == receiver,
                    CalibrationBucket.model == model,
                    CalibrationBucket.task_family == task_family,
                )
                .order_by(CalibrationBucket.bucket)
            )
        )

    def calibrated_probability(
        self,
        predicted: float,
        *,
        workspace: str = "default",
        receiver: str = "*",
        model: str = "*",
        task_family: str = "*",
    ) -> float:
        predicted = max(0.0, min(1.0, float(predicted)))
        bucket = self._bucket(predicted)
        item = self.db.scalar(
            select(CalibrationBucket).where(
                CalibrationBucket.workspace == workspace,
                CalibrationBucket.receiver == receiver,
                CalibrationBucket.model == model,
                CalibrationBucket.task_family == task_family,
                CalibrationBucket.bucket == bucket,
            )
        )
        if item is None or item.sample_count < self.min_samples:
            return predicted
        empirical = item.observed_sum / item.sample_count
        weight = item.sample_count / (item.sample_count + self.min_samples)
        return max(0.0, min(1.0, weight * empirical + (1.0 - weight) * predicted))

    def report(
        self,
        predicted: float,
        *,
        workspace: str = "default",
        receiver: str = "*",
        model: str = "*",
        task_family: str = "*",
    ) -> CalibrationReport:
        rows = self.rows(workspace=workspace, receiver=receiver, model=model, task_family=task_family)
        total = sum(row.sample_count for row in rows)
        if total == 0:
            return CalibrationReport(0, 0.0, 0.0, max(0.0, min(1.0, predicted)))
        ece = 0.0
        sse = 0.0
        for row in rows:
            if row.sample_count <= 0:
                continue
            mean_pred = row.predicted_sum / row.sample_count
            mean_obs = row.observed_sum / row.sample_count
            ece += (row.sample_count / total) * abs(mean_pred - mean_obs)
            sse += row.squared_error_sum
        return CalibrationReport(
            sample_count=total,
            expected_calibration_error=ece,
            brier_score=sse / total,
            calibrated_probability=self.calibrated_probability(
                predicted,
                workspace=workspace,
                receiver=receiver,
                model=model,
                task_family=task_family,
            ),
        )

    def response(self, report: CalibrationReport) -> dict[str, Any]:
        return {
            "sample_count": report.sample_count,
            "expected_calibration_error": report.expected_calibration_error,
            "brier_score": report.brier_score,
            "calibrated_probability": report.calibrated_probability,
        }
