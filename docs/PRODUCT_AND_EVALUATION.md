# Product and evaluation brief

## Problem and customer

Analysts and support teams often search across scattered product documentation. Keyword search misses paraphrases; ungrounded chat can sound confident while misrepresenting policy. The product question is: **which retrieval method gives this team useful, attributable answers for its actual questions and corpus, at an acceptable latency and cost?**

The prototype serves a technically curious analyst evaluating a document collection. Their job is to upload a representative corpus, ask a real question, switch retrieval methods, and judge the evidence before using the answer. It is not intended to make autonomous customer-impacting decisions.

## User workflow and product behavior

1. Add TXT, Markdown, or PDF files and review the accepted document/chunk counts.
2. Ask a question and select BM25, dense-vector, or hybrid retrieval in the dashboard.
3. Inspect ranked evidence, source names, and relevance scores before relying on the answer.
4. With an API key, generate a concise answer grounded only in retrieved excerpts and inspect its inline source references. Without a key, use BM25 and review evidence; generation and dense strategies are unavailable.
5. Compare strategies on the same query and report which evidence was missed or misleading.

## Algorithms and data

- **Chunking:** paragraph-aware splitting with configurable target size and overlap; retain document and chunk IDs for attribution.
- **BM25:** lexical term matching; interpretable, low-cost baseline that is strong for exact names and identifiers.
- **Dense vector:** OpenAI embedding cosine similarity; tests semantic matching and paraphrases, with provider/API dependency and embedding cost.
- **Hybrid:** reciprocal-rank fusion of lexical and dense rankings; may improve coverage but adds complexity and should not be assumed superior.
- **Generation:** answer only from selected evidence, cite chunk IDs, and explicitly abstain when evidence is insufficient.

The app accepts user-provided documents. Current prototype parsing covers PDF, TXT, and Markdown only. Scanned PDFs, tables, images, DOCX, access-control inheritance, and source freshness are not handled. A user's corpus is not automatically representative of all users.

## Success measures and validation plan

Phase 3 now provides a labeled synthetic fixture, reusable retrieval benchmark, and human answer-review rubric. These validate the evaluation workflow; product quality claims still wait for representative, permissioned data and human-reviewed generated answers.

| Dimension | Measure | Initial decision rule |
|---|---|---|
| Retrieval relevance | Recall@5, MRR@5, nDCG@5 against human-labeled supporting chunks | Compare each selectable strategy with BM25 on identical queries; report per-query failures and corpus slices. |
| Answer quality | Human rubric: correctness, completeness, groundedness, citation support, useful abstention | Blindly review sampled answers; do not use fluency as a correctness proxy. |
| Customer utility | Task completion / analyst rating and time to find a supported answer | Pilot with representative users and questions; keep a feedback reason, not just thumbs-up. |
| Reliability | Error rate, parse failures, timeout rate, p50/p95 latency | Track ingestion, retrieval, embedding, and generation separately. |
| Efficiency | Tokens and estimated API cost per question; latency by strategy | Compare quality/latency/cost Pareto frontier; set budgets before launch. |

Suggested pilot acceptance thresholds (to be ratified with stakeholders): ≥0.80 Recall@5 on the curated evidence set; ≥90% of reviewed answers fully supported by cited evidence; explicit abstention on ≥90% of deliberately unanswerable questions; p95 answer latency below 8 seconds at pilot load. Thresholds are hypotheses, not measured results.

## Experiment design

- Build a small but representative benchmark from real, permissioned queries and documents. Include paraphrases, exact identifiers, multi-document questions, unanswerable questions, stale/conflicting sources, and long-document cases.
- Have a domain reviewer label sufficient supporting chunks and acceptable answer criteria; independently double-label a sample and resolve disagreements.
- Compare BM25, dense, and hybrid with identical corpus, chunking, query set, top-k, and answer model. Report paired per-query differences and slices; include confidence intervals where sample size permits.
- Run chunk size/overlap and top-k ablations separately. Record model/index versions, configuration, latency, token usage, and cost for every run.
- Review errors with stakeholders; distinguish retrieval misses, bad source content, synthesis errors, and product UX failures before changing algorithms.

## Risks, limitations, and guardrails

- **Hallucination:** citation presence does not guarantee citation entailment. Show evidence and provide abstention; evaluate citation support.
- **Prompt injection in documents:** retrieved text is untrusted data. The prototype prompt says to ignore instructions in evidence, but this is not a complete security defense.
- **Privacy and tenancy:** prototype state is not a durable isolation boundary. Do not use sensitive documents; production needs identity, authorization filtering at retrieval, retention/deletion, and a privacy review.
- **Provider dependency:** dense and generated flows transmit query/content to the configured API provider; disclose this to users and configure approved services/models before deployment.
- **Evaluation bias:** curated examples can overstate quality. Include hard cases, multiple reviewers, and ongoing feedback.
- **Method selection:** user choice exposes tradeoffs, but it can confuse users. Preserve a simple explanation of each method and eventually recommend a method only after measured evidence.
