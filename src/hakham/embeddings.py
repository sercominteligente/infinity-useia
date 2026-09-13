from __future__ import annotations

import hashlib
import math
import re
import unicodedata
from abc import ABC, abstractmethod


class EmbeddingProvider(ABC):
    """Small provider contract for memory embeddings.

    Implementations may be fully local or remote. Retrieval code depends only
    on this interface, so HAKHAM is not locked to one model/vendor.
    """

    @abstractmethod
    def embed(self, text: str) -> list[float]:
        raise NotImplementedError


class HashEmbeddingProvider(EmbeddingProvider):
    """Deterministic local fallback embedding with no external dependency.

    This is not intended to compete with neural embeddings. It provides a
    stable vector seam for development, testing and offline fallback while a
    stronger local/remote provider can later be plugged in.
    """

    def __init__(self, dimensions: int = 256) -> None:
        if dimensions < 32:
            raise ValueError("dimensions must be at least 32")
        self.dimensions = dimensions

    @staticmethod
    def _tokens(text: str) -> list[str]:
        normalized = unicodedata.normalize("NFKD", text.casefold())
        normalized = "".join(ch for ch in normalized if not unicodedata.combining(ch))
        return [token for token in re.sub(r"[^a-z0-9]+", " ", normalized).split() if len(token) > 1]

    def embed(self, text: str) -> list[float]:
        vector = [0.0] * self.dimensions
        for token in self._tokens(text):
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            index = int.from_bytes(digest[:4], "big") % self.dimensions
            sign = 1.0 if digest[4] % 2 == 0 else -1.0
            vector[index] += sign
        norm = math.sqrt(sum(value * value for value in vector))
        if norm == 0:
            return vector
        return [value / norm for value in vector]


def cosine_similarity(left: list[float], right: list[float]) -> float:
    if len(left) != len(right):
        raise ValueError("embedding dimensions do not match")
    if not left:
        return 0.0
    left_norm = math.sqrt(sum(value * value for value in left))
    right_norm = math.sqrt(sum(value * value for value in right))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return sum(a * b for a, b in zip(left, right, strict=True)) / (left_norm * right_norm)
