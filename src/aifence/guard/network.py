# SPDX-FileCopyrightText: 2026 AIFENCE contributors
# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

import fnmatch
import ipaddress
import queue
import socket
import threading
from dataclasses import dataclass
from urllib.parse import quote, unquote, urlsplit, urlunsplit

from .errors import AuthorizationError, ConflictError


@dataclass(frozen=True)
class ValidatedEndpoint:
    canonical_url: str
    host: str
    port: int
    resolved_addresses: tuple[str, ...]
    network_zone: str
    resolution_timeout_seconds: int = 3


def _decode_until_stable(value: str, rounds: int = 3) -> str:
    current = value
    for _ in range(rounds):
        decoded = unquote(current)
        if decoded == current:
            return decoded
        current = decoded
    if unquote(current) != current:
        raise ConflictError("URL contains excessive nested percent encoding")
    return current


def canonical_path(value: str) -> str:
    if not value.startswith("/"):
        raise ConflictError("broker path must be absolute")
    decoded = _decode_until_stable(value)
    if any(character in decoded for character in ("\\", "\x00", "\r", "\n")):
        raise ConflictError("broker path contains prohibited characters")
    if "?" in decoded or "#" in decoded:
        raise ConflictError("broker path must not contain a query string or fragment")
    segments = decoded.split("/")
    if any(segment in {".", ".."} for segment in segments):
        raise ConflictError("broker path traversal is prohibited")
    if "//" in decoded:
        raise ConflictError("ambiguous empty URL path segments are prohibited")
    return quote(decoded, safe="/-._~!$&'()*+,;=:@")


def _host_allowed(host: str, patterns: tuple[str, ...]) -> bool:
    normalized = host.rstrip(".").lower()
    for pattern in patterns:
        candidate = pattern.rstrip(".").lower()
        if candidate.startswith("*."):
            suffix = candidate[1:]
            if normalized.endswith(suffix) and normalized != candidate[2:]:
                return True
        elif normalized == candidate:
            return True
    return False


def _address_zone(address: str) -> str:
    ip = ipaddress.ip_address(address)
    if (
        ip.is_private
        or ip.is_loopback
        or ip.is_link_local
        or ip.is_multicast
        or ip.is_reserved
        or ip.is_unspecified
    ):
        return "private"
    return "public"


_DNS_RESOLUTION_SLOTS = threading.BoundedSemaphore(32)


def resolve_host(host: str, port: int, *, timeout_seconds: int = 3) -> tuple[str, ...]:
    if not _DNS_RESOLUTION_SLOTS.acquire(timeout=timeout_seconds):
        raise ConflictError("broker DNS resolver capacity is exhausted")
    results: queue.Queue[tuple[list[tuple[object, ...]] | None, BaseException | None]] = queue.Queue(maxsize=1)

    def resolve() -> None:
        try:
            records = socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)
            results.put((records, None))
        except BaseException as exc:  # propagate resolver failures to the caller
            results.put((None, exc))
        finally:
            _DNS_RESOLUTION_SLOTS.release()

    thread = threading.Thread(target=resolve, name="aifence-dns", daemon=True)
    thread.start()
    try:
        records, error = results.get(timeout=timeout_seconds)
    except queue.Empty as exc:
        raise ConflictError("broker hostname resolution timed out") from exc
    if error is not None:
        raise ConflictError("broker hostname could not be resolved") from error
    assert records is not None
    addresses = sorted({record[4][0].split("%", 1)[0] for record in records})
    if not addresses:
        raise ConflictError("broker hostname resolved to no addresses")
    return tuple(addresses)


def validate_endpoint(
    url: str,
    *,
    allowed_hosts: tuple[str, ...],
    network_zone: str,
    require_resolution: bool = True,
    resolution_timeout_seconds: int = 3,
) -> ValidatedEndpoint:
    parsed = urlsplit(url)
    if parsed.scheme.lower() != "https":
        raise ConflictError("broker endpoints must use HTTPS")
    if parsed.username is not None or parsed.password is not None:
        raise ConflictError("broker endpoint user-info is prohibited")
    if parsed.query or parsed.fragment:
        raise ConflictError("broker base URL must not include query or fragment components")
    host = (parsed.hostname or "").rstrip(".").lower()
    if not host:
        raise ConflictError("broker endpoint hostname is missing")
    try:
        host.encode("ascii")
    except UnicodeEncodeError as exc:
        raise ConflictError("internationalized hostnames must be supplied in ASCII punycode") from exc
    if not allowed_hosts:
        raise AuthorizationError("deployment destination allowlist is empty")
    if not _host_allowed(host, allowed_hosts):
        raise AuthorizationError("broker hostname is not present in the deployment allowlist")
    port = parsed.port or 443
    if port != 443:
        raise ConflictError("broker endpoints must use TCP port 443")
    path = canonical_path(parsed.path or "/")
    addresses = (
        resolve_host(host, port, timeout_seconds=resolution_timeout_seconds)
        if require_resolution
        else ()
    )
    if addresses:
        observed_zones = {_address_zone(address) for address in addresses}
        if len(observed_zones) != 1:
            raise ConflictError("broker hostname resolves across public and private trust zones")
        observed_zone = next(iter(observed_zones))
        if observed_zone != network_zone:
            raise AuthorizationError(
                f"broker endpoint resolves to the {observed_zone} network zone, not {network_zone}"
            )
    netloc = host if port == 443 else f"{host}:{port}"
    canonical = urlunsplit(("https", netloc, path.rstrip("/") or "/", "", ""))
    return ValidatedEndpoint(canonical, host, port, addresses, network_zone, resolution_timeout_seconds)


def safe_join(base_url: str, path: str, allowed_patterns: list[str]) -> str:
    canonical = canonical_path(path)
    normalized_patterns = [canonical_path(pattern.replace("*", "AIFENCE_GUARD_WILDCARD"))
                           .replace("AIFENCE_GUARD_WILDCARD", "*") for pattern in allowed_patterns]
    if not any(fnmatch.fnmatchcase(canonical, pattern) for pattern in normalized_patterns):
        raise AuthorizationError("broker path is outside the registered allowlist")
    parsed = urlsplit(base_url)
    base_path = parsed.path.rstrip("/")
    joined_path = canonical_path(f"{base_path}{canonical}" if base_path else canonical)
    return urlunsplit((parsed.scheme, parsed.netloc, joined_path, "", ""))


def revalidate_resolution(endpoint: ValidatedEndpoint) -> None:
    if not endpoint.resolved_addresses:
        return
    current = set(resolve_host(
        endpoint.host, endpoint.port, timeout_seconds=endpoint.resolution_timeout_seconds
    ))
    expected = set(endpoint.resolved_addresses)
    if current != expected:
        raise AuthorizationError("broker DNS resolution changed after authorization")
    if any(_address_zone(address) != endpoint.network_zone for address in current):
        raise AuthorizationError("broker DNS resolution crossed a trust boundary")


def pin_validated_target(target: str, endpoint: ValidatedEndpoint) -> tuple[str, str, dict[str, str]]:
    """Revalidate DNS, then connect to an authorized IP while preserving HTTP host and TLS SNI.

    Returning the original target when resolution was intentionally skipped keeps non-production
    and test deployments usable. Production validation supplies resolved addresses, so the TCP
    connection no longer performs an uncontrolled third hostname lookup after authorization.
    """
    revalidate_resolution(endpoint)
    parsed = urlsplit(target)
    target_host = (parsed.hostname or "").rstrip(".").lower()
    if parsed.scheme.lower() != "https" or target_host != endpoint.host:
        raise AuthorizationError("broker target no longer matches the validated endpoint")
    if (parsed.port or 443) != endpoint.port:
        raise AuthorizationError("broker target port no longer matches the validated endpoint")
    if not endpoint.resolved_addresses:
        return target, endpoint.host, {}

    address = endpoint.resolved_addresses[0]
    parsed_ip = ipaddress.ip_address(address)
    host_literal = f"[{address}]" if parsed_ip.version == 6 else address
    netloc = host_literal if endpoint.port == 443 else f"{host_literal}:{endpoint.port}"
    pinned = urlunsplit((parsed.scheme, netloc, parsed.path, parsed.query, ""))
    return pinned, endpoint.host, {"sni_hostname": endpoint.host}
