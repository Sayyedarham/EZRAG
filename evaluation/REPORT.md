# Phase 3 benchmark report

## Run metadata

- Benchmark: `ezrag-synthetic-product-support-v1`
- Corpus: 12 curated synthetic evidence chunks
- Queries: 12 total; 11 answerable, one deliberately unanswerable
- Run: offline BM25; fixed benchmark chunks; top-k values 1, 3, and 5
- Reproduction: `python evaluation/run_benchmark.py --methods BM25 --top-k 1,3,5`
- Raw outputs: [`latest.json`](results/latest.json) and [`latest_per_query.csv`](results/latest_per_query.csv)

## Observed BM25 baseline

| k | Recall@k | MRR@k | nDCG@k | Mean retrieval latency |
|---:|---:|---:|---:|---:|
| 1 | 0.818 | 0.818 | 0.818 | 0.2 ms |
| 3 | 0.909 | 0.864 | 0.876 | 0.2 ms |
| 5 | 1.000 | 0.886 | 0.915 | 0.2 ms |

Scores average over 11 answerable synthetic questions. The latency is a single local run on this machine and excludes file parsing, network, answer generation, hosted load, and user-perceived UI time. It is not a service-level result.

## Interpretation

The run confirms that the benchmark reads labeled evidence, computes the metrics, preserves per-query ranked IDs, and emits the expected top-k output. The deliberately stale/conflicting case is not currently adversarial enough to validate freshness-aware ranking; chunk relevance labels only identify the current release note. One run, one tiny synthetic corpus, and fixed chunks cannot support a conclusion that BM25 is sufficient or that the proposed pilot thresholds are met in customer settings.

No dense/hybrid comparison or generated-answer/citation review is included in this checked-in run because those require an API key and human review. To compare the other methods, run the command in `evaluation/README.md` with an approved key. Paired intervals on this 11-query fixture remain descriptive, not inferential evidence about users. The monetary cost is not estimated; raw embedding token usage is recorded for API-enabled runs, and current account/model prices should be supplied by the project owner before cost comparison.

## Decision

Keep BM25 as the no-credential fallback, not as a quality-selected default. Phase 3's synthetic evaluation tooling is complete. Before making a retrieval recommendation, pass the production-data gate in [`README.md`](README.md): use permissioned representative questions/documents, independent labels, answer/citation review, reproducible paired runs, and production-shaped latency/cost measurements.
