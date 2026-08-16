# SPDX-FileCopyrightText: 2026 AGENTDANCE contributors
# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

import socket
import struct
from dataclasses import dataclass


@dataclass(frozen=True)
class ScanResult:
    status: str
    signature: str | None
    raw: str


class ClamAVClient:
    def __init__(self, host: str, port: int, timeout_seconds: int) -> None:
        self.host = host
        self.port = port
        self.timeout_seconds = timeout_seconds

    def ping(self) -> bool:
        try:
            with socket.create_connection((self.host, self.port), self.timeout_seconds) as sock:
                sock.sendall(b"zPING\0")
                response = sock.recv(64)
                return response.startswith(b"PONG")
        except OSError:
            return False

    def scan(self, content: bytes) -> ScanResult:
        with socket.create_connection((self.host, self.port), self.timeout_seconds) as sock:
            sock.sendall(b"zINSTREAM\0")
            view = memoryview(content)
            chunk_size = 64 * 1024
            for offset in range(0, len(content), chunk_size):
                chunk = view[offset : offset + chunk_size]
                sock.sendall(struct.pack("!I", len(chunk)))
                sock.sendall(chunk)
            sock.sendall(struct.pack("!I", 0))
            response = bytearray()
            while True:
                block = sock.recv(4096)
                if not block:
                    break
                response.extend(block)
                if b"\0" in block or b"\n" in block:
                    break
        raw = bytes(response).rstrip(b"\0\n").decode("utf-8", errors="replace")
        if raw.endswith(" OK"):
            return ScanResult("clean", None, raw)
        if raw.endswith(" FOUND"):
            signature = raw.rsplit(": ", 1)[-1].removesuffix(" FOUND")
            return ScanResult("infected", signature, raw)
        return ScanResult("error", None, raw)
