"""Stable per-game model-request seeds for paired Duck experiments."""

from __future__ import annotations

import hashlib


MAX_SEED = 2_147_483_647


def stable_request_seed(namespace: str, request_index: int, salt: str) -> int:
    """Return a stable non-negative seed independent of process scheduling."""
    payload = f"{salt}:{namespace}:{int(request_index)}".encode("utf-8")
    digest = hashlib.sha256(payload).digest()
    return int.from_bytes(digest[:8], "big") % MAX_SEED


class RequestSeedSequence:
    """Issue one deterministic seed per request for a single game session."""

    def __init__(
        self,
        namespace: str | None,
        *,
        salt: str,
        fallback_seed: int = -1,
    ) -> None:
        self.namespace = str(namespace or "").strip()
        self.salt = str(salt)
        self.fallback_seed = int(fallback_seed)
        self.request_index = 0

    def next_seed(self) -> int:
        if not self.namespace:
            return self.fallback_seed
        seed = stable_request_seed(self.namespace, self.request_index, self.salt)
        self.request_index += 1
        return seed
