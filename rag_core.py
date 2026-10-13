"""Shared retrieval algorithms for the app and offline benchmark runner."""

from __future__ import annotations

import math
import re
from collections import Counter
from typing import Any

from openai import OpenAI

EMBED_MODEL = "text-embedding-3-small"


def tokenize(text: str) -> list[str]:
    return re.findall(r"[\w-]+", text.casefold())


def bm25_scores(query: str, chunks: list[dict[str, Any]]) -> list[float]:
    query_terms = tokenize(query)
    docs = [tokenize(chunk["text"]) for chunk in chunks]
    n_docs = len(docs)
    if not n_docs:
        return []
    avg_len = sum(map(len, docs)) / n_docs or 1.0
    document_frequency: Counter[str] = Counter()
    for terms in docs:
        document_frequency.update(set(terms))
    scores = []
    k1, b = 1.5, 0.75
    for terms in docs:
        counts = Counter(terms)
        score = 0.0
        for term in query_terms:
            df = document_frequency.get(term, 0)
            if not df:
                continue
            idf = math.log(1 + (n_docs - df + 0.5) / (df + 0.5))
            frequency = counts[term]
            score += idf * frequency * (k1 + 1) / (
                frequency + k1 * (1 - b + b * len(terms) / avg_len)
            )
        scores.append(score)
    return scores


def ensure_embeddings(client: OpenAI, chunks: list[dict[str, Any]], model: str = EMBED_MODEL) -> int:
    """Embed missing chunks in bounded requests; return API-reported token usage."""
    missing = [chunk for chunk in chunks if "embedding" not in chunk]
    tokens = 0
    for offset in range(0, len(missing), 64):
        batch = missing[offset : offset + 64]
        result = client.embeddings.create(model=model, input=[item["text"] for item in batch])
        tokens += getattr(result.usage, "total_tokens", 0) if result.usage else 0
        for item, record in zip(batch, result.data):
            item["embedding"] = record.embedding
    return tokens


def cosine(left: list[float], right: list[float]) -> float:
    dot = sum(a * b for a, b in zip(left, right))
    left_norm = math.sqrt(sum(value * value for value in left))
    right_norm = math.sqrt(sum(value * value for value in right))
    return dot / (left_norm * right_norm) if left_norm and right_norm else 0.0


def rank_chunks(
    query: str,
    chunks: list[dict[str, Any]],
    method: str,
    client: OpenAI | None,
    top_k: int,
    embedding_model: str = EMBED_MODEL,
    rrf_k: int = 60,
) -> tuple[list[dict[str, Any]], int]:
    """Return ranked chunks and newly incurred embedding-token usage."""
    lexical = bm25_scores(query, chunks)
    lexical_order = sorted(range(len(chunks)), key=lambda i: lexical[i], reverse=True)
    embedding_tokens = 0
    if method == "BM25":
        # Returning arbitrary zero-score passages invites unsupported answers.
        ranked = [
            (index, lexical[index], "BM25")
            for index in lexical_order
            if lexical[index] > 0
        ][:top_k]
    else:
        if client is None:
            raise ValueError("An OpenAI API key is required for dense and hybrid retrieval.")
        embedding_tokens += ensure_embeddings(client, chunks, embedding_model)
        result = client.embeddings.create(model=embedding_model, input=[query])
        embedding_tokens += getattr(result.usage, "total_tokens", 0) if result.usage else 0
        query_embedding = result.data[0].embedding
        dense_scores = [cosine(query_embedding, chunk["embedding"]) for chunk in chunks]
        dense_order = sorted(range(len(chunks)), key=lambda i: dense_scores[i], reverse=True)
        if method == "Dense vector":
            ranked = [(index, dense_scores[index], "Cosine similarity") for index in dense_order[:top_k]]
        elif method == "Hybrid (RRF)":
            fused: dict[int, float] = {}
            for order in (lexical_order, dense_order):
                for rank, index in enumerate(order, start=1):
                    fused[index] = fused.get(index, 0.0) + 1.0 / (rrf_k + rank)
            order = sorted(fused, key=fused.get, reverse=True)
            ranked = [(index, fused[index], "RRF") for index in order[:top_k]]
        else:
            raise ValueError(f"Unknown retrieval method: {method}")
    return [
        {**chunks[index], "score": score, "score_type": score_type}
        for index, score, score_type in ranked
    ], embedding_tokens
