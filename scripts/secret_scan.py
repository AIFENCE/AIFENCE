#!/usr/bin/env python3
"""Deterministic secret scan for tracked/source files.

This intentionally complements (rather than replaces) GitHub secret scanning. It
catches high-confidence credential formats and private keys without requiring a
third-party SaaS/license in CI.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED_PARTS = {'.git', '.venv', 'node_modules', 'dist', 'build', '__pycache__', '.pytest_cache'}
TEXT_SUFFIXES = {'.py','.toml','.yml','.yaml','.json','.md','.txt','.sh','.js','.ts','.tsx','.go','.html','.css','.ini','.cfg','.env'}
PATTERNS = {
    'private-key': re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----'),
    'github-token': re.compile(r'\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{30,}\b'),
    'github-fine-grained': re.compile(r'\bgithub_pat_[A-Za-z0-9_]{40,}\b'),
    'aws-access-key': re.compile(r'\b(?:AKIA|ASIA)[A-Z0-9]{16}\b'),
    'openai-key': re.compile(r'\bsk-(?:proj-)?[A-Za-z0-9_-]{32,}\b'),
    'generic-bearer': re.compile(r'(?i)authorization\s*[:=]\s*["\']?bearer\s+[A-Za-z0-9._~+/=-]{24,}'),
}
ALLOW_MARKERS = ('example', 'placeholder', 'changeme', '<token>', '${', '***', 'test-secret', 'dummy')
ALLOWLIST = ROOT / '.secret-scan-allowlist'


def candidates() -> list[Path]:
    result: list[Path] = []
    for path in ROOT.rglob('*'):
        if not path.is_file() or any(p in EXCLUDED_PARTS for p in path.relative_to(ROOT).parts):
            continue
        if path.suffix.lower() in TEXT_SUFFIXES or path.name in {'.env.example', '.gitignore'}:
            result.append(path)
    return sorted(result)


def _allowlist() -> set[tuple[str, str]]:
    if not ALLOWLIST.is_file():
        return set()
    result: set[tuple[str, str]] = set()
    for raw in ALLOWLIST.read_text(encoding='utf-8').splitlines():
        line = raw.strip()
        if not line or line.startswith('#'):
            continue
        path, sep, kind = line.partition('|')
        if not sep:
            raise SystemExit(f'invalid secret-scan allowlist entry: {raw}')
        result.add((path, kind))
    return result

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--quiet', action='store_true')
    args = parser.parse_args()
    findings: list[str] = []
    allowed = _allowlist()
    for path in candidates():
        try:
            text = path.read_text(encoding='utf-8')
        except (UnicodeDecodeError, OSError):
            continue
        rel = path.relative_to(ROOT)
        for lineno, line in enumerate(text.splitlines(), 1):
            lower = line.lower()
            for name, pattern in PATTERNS.items():
                if not pattern.search(line):
                    continue
                if any(marker in lower for marker in ALLOW_MARKERS):
                    continue
                if (rel.as_posix(), name) in allowed:
                    continue
                findings.append(f'{rel}:{lineno}: possible {name}')
    if findings:
        raise SystemExit('secret scan failed:\n' + '\n'.join(findings))
    if not args.quiet:
        print(f'secret scan PASS ({len(candidates())} text files)')

if __name__ == '__main__':
    main()
