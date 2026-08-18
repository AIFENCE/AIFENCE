# SPDX-FileCopyrightText: 2026 AIFENCE contributors
# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

import io
import zipfile
from dataclasses import dataclass
from pathlib import PurePosixPath
from typing import Any


@dataclass(frozen=True)
class ArtifactAnalysis:
    safe_to_release: bool
    detected_type: str
    findings: list[dict[str, Any]]


def _detected_type(content: bytes) -> str:
    if content.startswith(b"PK\x03\x04"):
        return "application/zip"
    if content.startswith(b"%PDF-"):
        return "application/pdf"
    if content.startswith(b"\x7fELF"):
        return "application/x-elf"
    if content.startswith(b"MZ"):
        return "application/vnd.microsoft.portable-executable"
    if content.startswith((b"\x89PNG\r\n\x1a\n",)):
        return "image/png"
    if content.startswith((b"GIF87a", b"GIF89a")):
        return "image/gif"
    if content.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    return "application/octet-stream"


def _inspect_zip(
    content: bytes,
    *,
    depth: int,
    max_depth: int,
    max_entries: int,
    max_uncompressed_bytes: int,
    max_ratio: int,
) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    if depth > max_depth:
        return [{"category": "archive.depth_exceeded", "severity": "high", "depth": depth}]
    try:
        archive = zipfile.ZipFile(io.BytesIO(content))
    except (zipfile.BadZipFile, OSError):
        return [{"category": "archive.invalid", "severity": "high"}]
    with archive:
        infos = archive.infolist()
        if len(infos) > max_entries:
            findings.append(
                {
                    "category": "archive.entry_limit_exceeded",
                    "severity": "high",
                    "entries": len(infos),
                    "max_entries": max_entries,
                }
            )
            return findings
        total_uncompressed = 0
        total_compressed = 0
        for info in infos:
            name = info.filename.replace("\\", "/")
            path = PurePosixPath(name)
            if path.is_absolute() or ".." in path.parts or "\x00" in name:
                findings.append(
                    {"category": "archive.path_traversal", "severity": "critical", "entry": name[:512]}
                )
            if info.flag_bits & 0x1:
                findings.append(
                    {"category": "archive.encrypted_entry", "severity": "high", "entry": name[:512]}
                )
            mode = (info.external_attr >> 16) & 0o170000
            if mode == 0o120000:
                findings.append(
                    {"category": "archive.symbolic_link", "severity": "high", "entry": name[:512]}
                )
            total_uncompressed += info.file_size
            total_compressed += max(1, info.compress_size)
            if total_uncompressed > max_uncompressed_bytes:
                findings.append(
                    {
                        "category": "archive.expansion_limit_exceeded",
                        "severity": "critical",
                        "uncompressed_bytes": total_uncompressed,
                        "max_uncompressed_bytes": max_uncompressed_bytes,
                    }
                )
                return findings
            if info.file_size > 0 and info.file_size / max(1, info.compress_size) > max_ratio:
                findings.append(
                    {
                        "category": "archive.compression_ratio_exceeded",
                        "severity": "critical",
                        "entry": name[:512],
                        "ratio": round(info.file_size / max(1, info.compress_size), 2),
                    }
                )
            if name.lower().endswith((".zip", ".jar", ".whl")) and info.file_size <= max_uncompressed_bytes:
                try:
                    nested = archive.read(info, pwd=None)
                except (RuntimeError, OSError, zipfile.BadZipFile):
                    findings.append(
                        {"category": "archive.nested_unreadable", "severity": "high", "entry": name[:512]}
                    )
                else:
                    findings.extend(
                        _inspect_zip(
                            nested,
                            depth=depth + 1,
                            max_depth=max_depth,
                            max_entries=max_entries,
                            max_uncompressed_bytes=max_uncompressed_bytes,
                            max_ratio=max_ratio,
                        )
                    )
        if total_uncompressed / max(1, total_compressed) > max_ratio:
            findings.append(
                {
                    "category": "archive.aggregate_ratio_exceeded",
                    "severity": "critical",
                    "ratio": round(total_uncompressed / max(1, total_compressed), 2),
                }
            )
    return findings


def analyze_artifact(
    content: bytes,
    *,
    declared_media_type: str,
    max_uncompressed_bytes: int,
    max_entries: int = 1000,
    max_archive_depth: int = 3,
    max_compression_ratio: int = 100,
) -> ArtifactAnalysis:
    detected = _detected_type(content)
    findings: list[dict[str, Any]] = []
    normalized_declared = declared_media_type.split(";", 1)[0].strip().lower()
    if (
        detected != "application/octet-stream"
        and normalized_declared not in {detected, "application/octet-stream"}
    ):
        findings.append(
            {
                "category": "content_type.mismatch",
                "severity": "medium",
                "declared": normalized_declared,
                "detected": detected,
            }
        )
    if detected == "application/zip":
        findings.extend(
            _inspect_zip(
                content,
                depth=1,
                max_depth=max_archive_depth,
                max_entries=max_entries,
                max_uncompressed_bytes=max_uncompressed_bytes,
                max_ratio=max_compression_ratio,
            )
        )
    if detected in {"application/x-elf", "application/vnd.microsoft.portable-executable"}:
        findings.append(
            {
                "category": "executable.binary",
                "severity": "high",
                "detected": detected,
            }
        )
    unsafe = any(finding.get("severity") in {"high", "critical"} for finding in findings)
    return ArtifactAnalysis(not unsafe, detected, findings)
