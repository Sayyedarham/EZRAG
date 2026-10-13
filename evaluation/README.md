# Phase 3 benchmark

## Run

From the repository root:

```bash
python evaluation/run_benchmark.py --methods "BM25,Dense vector,Hybrid (RRF)" --top-k 1,3,5 --rrf-k 10,60,100
```

`BM25` runs fully offline. Dense and hybrid methods require `OPENAI_API_KEY` and use `OPENAI_EMBEDDING_MODEL` (default `text-embedding-3-small`). The runner embeds corpus chunks once per process, records newly incurred embedding token usage and query latency, and writes a reproducible JSON plus per-query CSV under `evaluation/results/`. Results contain retrieved and relevant chunk IDs for error analysis. Keys are not written to results.

The fixture has 12 hand-labeled synthetic queries across exact identifiers, paraphrases, multi-evidence, stale/conflicting information, and unanswerable questions. Relevance metrics exclude unanswerable questions; those cases remain in the raw run for answerability/abstention review. The fixture is intentionally small and synthetic, so its confidence intervals describe only this toy set and do not support customer-quality conclusions.

## Metrics and comparisons

- Recall@k counts the fraction of labeled supporting chunks present in the first k results.
- MRR@k is the reciprocal rank of the first relevant chunk (zero on a miss).
- nDCG@k uses binary chunk relevance and discounts lower ranks.
- Paired deltas compare each method with BM25 on the same answerable query IDs. A deterministic, query-level paired bootstrap gives a 95% percentile interval. With 11 answerable queries, intervals are descriptive only.
- Latency is local retrieval wall time for BM25 and end-to-end embedding-plus-retrieval wall time for dense/hybrid; it is not generation latency or hosted load-test latency. Embedding token usage is recorded; monetary cost is intentionally omitted because rates vary by account/model and can change.
- `--top-k` supports a top-k ablation. `--rrf-k` supports fusion-constant ablations. The fixture uses fixed labeled chunks, so chunk-size/overlap ablations require a separately labeled raw-document benchmark and are not claimed here.

## Answer quality review

Retrieval metrics cannot validate generated answer correctness or citation entailment. Use `answer_review_template.csv` to blind-review answers from a permissioned, human-curated set. Score correctness, completeness, groundedness, and citation support from 0 (fails) to 2 (meets); record appropriate abstention and a failure category. Double-review a sample and resolve disagreements before publishing claims. Do not populate the template with synthetic answers and call them user findings.

## Production-data gate

Before making a product-method recommendation, replace/extend the fixture with permissioned representative queries and chunk IDs, obtain independent domain labels, pre-register slices and acceptance criteria, run paired comparisons, and report the benchmark date, model/index/configuration, sample size, and uncertainty. Run generation/citation review and load testing separately.
