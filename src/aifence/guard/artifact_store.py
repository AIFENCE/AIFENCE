# SPDX-FileCopyrightText: 2026 AIFENCE contributors
# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Protocol
from urllib.parse import urlparse


class ArtifactStore(Protocol):
    def put(self, tenant_id: str, artifact_id: str, content: bytes) -> str: ...
    def put_object(self, tenant_id: str, namespace: str, object_id: str, content: bytes,
                   *, metadata: dict[str, str] | None = None) -> str: ...
    def get(self, storage_key: str) -> bytes: ...
    def delete(self, storage_key: str) -> None: ...


class DisabledArtifactStore:
    """Fail-closed store for runtimes that are not authorized to access artifacts."""
    def put(self, tenant_id: str, artifact_id: str, content: bytes) -> str:
        raise PermissionError("this runtime is not authorized for artifact storage")
    def put_object(self, tenant_id: str, namespace: str, object_id: str, content: bytes,
                   *, metadata: dict[str, str] | None = None) -> str:
        raise PermissionError("this runtime is not authorized for evidence storage")
    def get(self, storage_key: str) -> bytes:
        raise PermissionError("this runtime is not authorized for artifact storage")
    def delete(self, storage_key: str) -> None:
        raise PermissionError("this runtime is not authorized for artifact storage")


class FileArtifactStore:
    """Encrypted blob store with atomic, non-following filesystem writes."""
    def __init__(self, root: str) -> None:
        self.root = Path(root).expanduser().resolve()
        self.root.mkdir(parents=True, exist_ok=True, mode=0o700)
    @staticmethod
    def _component(value: str) -> str:
        valid = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-"
        if not value or any(ch not in valid for ch in value):
            raise ValueError("artifact storage identifier is invalid")
        return value
    def put(self, tenant_id: str, artifact_id: str, content: bytes) -> str:
        return self._put_path(tenant_id, None, artifact_id, content)

    def put_object(self, tenant_id: str, namespace: str, object_id: str, content: bytes,
                   *, metadata: dict[str, str] | None = None) -> str:
        del metadata
        return self._put_path(tenant_id, namespace, object_id, content)

    def _put_path(self, tenant_id: str, namespace: str | None, object_id: str,
                  content: bytes) -> str:
        tenant = self._component(tenant_id); object_name = self._component(object_id)
        parts = [tenant]
        if namespace is not None:
            parts.append(self._component(namespace))
        relative = "/".join((*parts, f"{object_name}.enc"))
        directory = self.root.joinpath(*parts); directory.mkdir(mode=0o700, parents=True, exist_ok=True)
        target = directory / f"{object_name}.enc"; temporary = directory / f".{object_name}.{os.getpid()}.tmp"
        fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0), 0o600)
        try:
            with os.fdopen(fd, "wb") as handle:
                handle.write(content); handle.flush(); os.fsync(handle.fileno())
            os.replace(temporary, target)
            # Best-effort directory fsync for crash durability. Some platforms
            # (notably Windows) do not permit opening a directory as a file
            # descriptor; the atomic os.replace above still holds there.
            try:
                directory_fd = os.open(directory, os.O_RDONLY)
            except (PermissionError, OSError):
                directory_fd = None
            if directory_fd is not None:
                try: os.fsync(directory_fd)
                finally: os.close(directory_fd)
        finally:
            temporary.unlink(missing_ok=True)
        return relative
    def get(self, storage_key: str) -> bytes:
        path = (self.root / storage_key).resolve()
        if self.root not in path.parents: raise ValueError("artifact storage key escapes the configured root")
        fd = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
        with os.fdopen(fd, "rb") as handle: return handle.read()
    def delete(self, storage_key: str) -> None:
        path = (self.root / storage_key).resolve()
        if self.root not in path.parents: raise ValueError("artifact storage key escapes the configured root")
        path.unlink(missing_ok=True)


class S3ArtifactStore:
    """Credential-native S3 evidence store using the official provider SDK.

    Workload credentials are used by default. Static credentials remain optional
    for compatibility but are never required. Reads are streamed and bounded;
    deletes are disabled unless an explicit lifecycle worker enables them.
    """

    def __init__(
        self,
        *,
        endpoint: str,
        bucket: str,
        region: str,
        access_key: str = "",
        secret_key: str = "",
        prefix: str = "aifence",
        kms_key_id: str = "",
        object_lock_days: int = 0,
        delete_enabled: bool = False,
        max_object_bytes: int = 32 * 1024 * 1024,
        client: object | None = None,
    ) -> None:
        parsed = urlparse(endpoint)
        if (parsed.scheme not in {"https", "http"} or not parsed.hostname
                or parsed.username is not None or parsed.password is not None
                or parsed.path not in {"", "/"} or parsed.query or parsed.fragment):
            raise ValueError("S3 endpoint must be a canonical HTTP(S) origin")
        if not bucket or "/" in bucket:
            raise ValueError("S3 bucket is required")
        if bool(access_key) != bool(secret_key):
            raise ValueError("S3 static credentials must be supplied as a complete pair")
        if max_object_bytes < 1024:
            raise ValueError("S3 maximum object size is too small")
        self.endpoint = endpoint.rstrip("/")
        self.bucket = bucket
        self.region = region
        self.prefix = prefix.strip("/")
        self.kms_key_id = kms_key_id
        self.object_lock_days = max(object_lock_days, 0)
        self.delete_enabled = delete_enabled
        self.max_object_bytes = max_object_bytes
        if client is None:
            try:
                import boto3
                from botocore.config import Config
            except ImportError as exc:
                raise RuntimeError("S3 artifact storage requires the boto3 package") from exc
            kwargs: dict[str, object] = {
                "service_name": "s3",
                "endpoint_url": self.endpoint,
                "region_name": self.region,
                "config": Config(
                    signature_version="s3v4",
                    retries={"max_attempts": 4, "mode": "adaptive"},
                    connect_timeout=10,
                    read_timeout=60,
                ),
            }
            if access_key:
                kwargs["aws_access_key_id"] = access_key
                kwargs["aws_secret_access_key"] = secret_key
            client = boto3.client(**kwargs)
        self.client = client

    @staticmethod
    def _component(value: str) -> str:
        if not value or any(ch not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-" for ch in value):
            raise ValueError("artifact storage identifier is invalid")
        return value

    def _key(self, tenant_id: str, object_id: str, namespace: str | None = None) -> str:
        parts = [self.prefix, self._component(tenant_id)]
        if namespace is not None:
            parts.append(self._component(namespace))
        parts.append(f"{self._component(object_id)}.enc")
        return "/".join(filter(None, parts))

    def put(self, tenant_id: str, artifact_id: str, content: bytes) -> str:
        return self._put_object(tenant_id, None, artifact_id, content, metadata=None)

    def put_object(self, tenant_id: str, namespace: str, object_id: str, content: bytes,
                   *, metadata: dict[str, str] | None = None) -> str:
        return self._put_object(tenant_id, namespace, object_id, content, metadata=metadata)

    def _put_object(self, tenant_id: str, namespace: str | None, object_id: str,
                    content: bytes, *, metadata: dict[str, str] | None) -> str:
        if len(content) > self.max_object_bytes:
            raise ValueError("evidence ciphertext exceeds the configured object limit")
        key = self._key(tenant_id, object_id, namespace)
        request: dict[str, object] = {
            "Bucket": self.bucket,
            "Key": key,
            "Body": content,
            "ContentType": "application/octet-stream",
            "IfNoneMatch": "*",
            "Metadata": {
                "aifence-tenant": tenant_id,
                "aifence-object": object_id,
                "aifence-namespace": namespace or "artifacts",
                **(metadata or {}),
            },
        }
        if self.kms_key_id:
            request.update({
                "ServerSideEncryption": "aws:kms",
                "SSEKMSKeyId": self.kms_key_id,
                "SSEKMSEncryptionContext": __import__("json").dumps(
                    {"tenant_id": tenant_id, "namespace": namespace or "artifacts", "object_id": object_id},
                    sort_keys=True, separators=(",", ":"),
                ),
                "BucketKeyEnabled": True,
            })
        else:
            request["ServerSideEncryption"] = "AES256"
        if self.object_lock_days:
            from datetime import timedelta
            request.update({
                "ObjectLockMode": "COMPLIANCE",
                "ObjectLockRetainUntilDate": datetime.now(UTC) + timedelta(days=self.object_lock_days),
            })
        self.client.put_object(**request)
        return key

    def get(self, storage_key: str) -> bytes:
        response = self.client.get_object(Bucket=self.bucket, Key=storage_key)
        declared = int(response.get("ContentLength", 0) or 0)
        if declared > self.max_object_bytes:
            raise ValueError("artifact ciphertext exceeds the configured object limit")
        body = response["Body"]
        chunks: list[bytes] = []
        total = 0
        try:
            while True:
                chunk = body.read(min(1024 * 1024, self.max_object_bytes - total + 1))
                if not chunk:
                    break
                total += len(chunk)
                if total > self.max_object_bytes:
                    raise ValueError("artifact ciphertext exceeds the configured object limit")
                chunks.append(bytes(chunk))
        finally:
            close = getattr(body, "close", None)
            if callable(close):
                close()
        return b"".join(chunks)

    def delete(self, storage_key: str) -> None:
        if not self.delete_enabled:
            raise PermissionError("artifact deletion is disabled; use the governed retention lifecycle")
        self.client.delete_object(Bucket=self.bucket, Key=storage_key)
