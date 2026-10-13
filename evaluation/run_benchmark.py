"""Run retrieval comparisons over the versioned JSON benchmark fixture."""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import random
import statistics
import sys
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from openai import OpenAI

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from rag_core import rank_chunks  # noqa: E402

DATA_PATH = Path(__file__).with_name("benchmark.json")
RESULTS_DIR = Path(__file__).with_name("results")
METHODS = ["BM25", "Dense vector", "Hybrid (RRF)"]


def metrics(retrieved: list[str], relevant: list[str], k: int) -> dict[str, float | None]:
    if not relevant:
        return {"recall": None, "mrr": None, "ndcg": None}
    selected = retrieved[:k]
    relevant_set = set(relevant)
    hits = [1 if item in relevant_set else 0 for item in selected]
    recall = sum(hits) / len(relevant_set)
    reciprocal_rank = next((1 / rank for rank, hit in enumerate(hits, start=1) if hit), 0.0)
    dcg = sum(hit / math.log2(rank + 1) for rank, hit in enumerate(hits, start=1))
    ideal_hits = min(len(relevant_set), k)
    ideal_dcg = sum(1 / math.log2(rank + 1) for rank in range(1, ideal_hits + 1))
    return {"recall": recall, "mrr": reciprocal_rank, "ndcg": dcg / ideal_dcg if ideal_dcg else 0.0}


def mean(values: list[float]) -> float | None:
    return statistics.fmean(values) if values else None


def bootstrap_delta_ci(deltas: list[float], seed: int = 42017, iterations: int = 2000) -> list[float] | None:
    if not deltas:
        return None
    rng = random.Random(seed)
    n = len(deltas)
    means = sorted(statistics.fmean(rng.choices(deltas, k=n)) for _ in range(iterations))
    return [means[int(0.025 * iterations)], means[min(iterations - 1, int(0.975 * iterations))]]


def aggregate(rows: list[dict[str, Any]], key: str) -> float | None:
    return mean([row[key] for row in rows if row[key] is not None])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--methods", default="BM25,Dense vector,Hybrid (RRF)", help="Comma-separated method names.")
    parser.add_argument("--top-k", default="1,3,5", help="Comma-separated k values for top-k ablation.")
    parser.add_argument("--rrf-k", default="60", help="Comma-separated RRF constants for fusion ablation.")
    parser.add_argument("--output-dir", type=Path, default=RESULTS_DIR)
    args = parser.parse_args()

    methods = [item.strip() for item in args.methods.split(",") if item.strip()]
    top_ks = sorted(set(int(item) for item in args.top_k.split(",")))
    rrf_ks = sorted(set(int(item) for item in args.rrf_k.split(",")))
    if set(methods) - set(METHODS) or any(k < 1 for k in top_ks) or any(k < 1 for k in rrf_ks):
        parser.error("Use known methods and positive top-k/RRF values.")
    if any(method != "BM25" for method in methods) and not os.getenv("OPENAI_API_KEY"):
        parser.error("Dense and hybrid runs require OPENAI_API_KEY; choose --methods BM25 for offline mode.")

    benchmark = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    chunks = [dict(item) for item in benchmark["chunks"]]
    queries = benchmark["queries"]
    client = OpenAI() if os.getenv("OPENAI_API_KEY") else None
    embedding_model = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
    rows: list[dict[str, Any]] = []
    rrf_grid = rrf_ks if "Hybrid (RRF)" in methods else [60]

    for method in methods:
        for rrf_k in rrf_grid:
            for query in queries:
                start = time.perf_counter()
                try:
                    ranked, embedding_tokens = rank_chunks(
                        query["query"], chunks, method, client, max(top_ks), embedding_model, rrf_k
                    )
                    elapsed_ms = (time.perf_counter() - start) * 1000
                    retrieved_ids = [item["id"] for item in ranked]
                    for k in top_ks:
                        score = metrics(retrieved_ids, query["relevant_chunk_ids"], k)
                        rows.append({
                            "query_id": query["id"], "slice": query["slice"], "answerable": query["answerable"],
                            "method": method, "rrf_k": rrf_k if method == "Hybrid (RRF)" else None,
                            "top_k": k, "recall": score["recall"], "mrr": score["mrr"], "ndcg": score["ndcg"],
                            "latency_ms": elapsed_ms, "embedding_tokens": embedding_tokens,
                            "retrieved_chunk_ids": retrieved_ids[:k],
                            "relevant_chunk_ids": query["relevant_chunk_ids"],
                        })
                except Exception as exc:
                    print(f"Failed {method} / {query['id']}: {exc}", file=sys.stderr)
                    return 2

    # Aggregate means by method, query slice, and each k. Unanswerable cases remain in raw output
    # for later abstention review and are intentionally excluded from relevance metric means.
    summaries = []
    groups: dict[tuple[str, int | None, int, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[(row["method"], row["rrf_k"], row["top_k"], "overall")].append(row)
        groups[(row["method"], row["rrf_k"], row["top_k"], row["slice"])].append(row)
    for (method, rrf_k, k, slice_name), grouped in sorted(groups.items(), key=lambda x: str(x[0])):
        summaries.append({
            "method": method, "rrf_k": rrf_k, "top_k": k, "slice": slice_name,
            "n_queries": len(grouped), "n_answerable": sum(row["answerable"] for row in grouped),
            "recall": aggregate(grouped, "recall"), "mrr": aggregate(grouped, "mrr"),
            "ndcg": aggregate(grouped, "ndcg"), "mean_latency_ms": mean([row["latency_ms"] for row in grouped]),
            "p50_latency_ms": statistics.median([row["latency_ms"] for row in grouped]),
            "p95_latency_ms": sorted(row["latency_ms"] for row in grouped)[
                min(len(grouped) - 1, math.ceil(0.95 * len(grouped)) - 1)
            ],
            "embedding_tokens": sum(row["embedding_tokens"] for row in grouped),
        })

    paired: list[dict[str, Any]] = []
    for method in methods:
        if method == "BM25":
            continue
        for k in top_ks:
            for metric_name in ("recall", "mrr", "ndcg"):
                base = {row["query_id"]: row[metric_name] for row in rows
                        if row["method"] == "BM25" and row["top_k"] == k and row[metric_name] is not None}
                method_rrf_values = sorted({row["rrf_k"] for row in rows if row["method"] == method})
                for rrf_k in method_rrf_values:
                    target = {row["query_id"]: row[metric_name] for row in rows
                              if row["method"] == method and row["rrf_k"] == rrf_k
                              and row["top_k"] == k and row[metric_name] is not None}
                    deltas = [target[key] - base[key] for key in target.keys() & base.keys()]
                    paired.append({
                        "method": method, "rrf_k": rrf_k, "top_k": k, "metric": metric_name,
                        "n_paired": len(deltas), "mean_delta_vs_bm25": mean(deltas),
                        "bootstrap_95pct_ci": bootstrap_delta_ci(deltas),
                    })

    args.output_dir.mkdir(parents=True, exist_ok=True)
    run = {
        "benchmark_id": benchmark["benchmark_id"],
        "benchmark_description": benchmark["description"],
        "run_timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "configuration": {"methods": methods, "top_ks": top_ks, "rrf_ks": rrf_grid,
                          "embedding_model": embedding_model if client else None,
                          "answer_model": None, "chunking": "fixed curated chunks; no chunking ablation in this fixture"},
        "interpretation": "Synthetic benchmark plumbing only. Not representative user data and not a product quality claim.",
        "summaries": summaries, "paired_deltas_vs_bm25": paired, "per_query": rows,
    }
    json_path = args.output_dir / "latest.json"
    json_path.write_text(json.dumps(run, indent=2), encoding="utf-8")
    csv_path = args.output_dir / "latest_per_query.csv"
    if rows:
        with csv_path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
    print(f"Wrote {json_path} and {csv_path}")
    for item in summaries:
        if item["slice"] == "overall":
            print(f"{item['method']} rrf={item['rrf_k']} k={item['top_k']}: "
                  f"Recall={item['recall']:.3f} MRR={item['mrr']:.3f} nDCG={item['ndcg']:.3f} "
                  f"mean-query-latency={item['mean_latency_ms']:.1f}ms n={item['n_answerable']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
