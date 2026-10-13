# Six-phase delivery roadmap

## Product goal

Help a product or support analyst answer questions over a trusted document collection, see why a response was produced, and select retrieval behavior that fits the question and corpus. The differentiator is a visible, controlled comparison of RAG methodologies with evidence and evaluation—not an opaque chat demo.

| Phase | Name | Outcomes | Exit criteria |
|---|---|---|---|
| **1 — Define** | Problem, users, risks, and measurement (**complete**) | Product brief; user journey; data boundaries; retrieval strategy definitions; benchmark and success metrics; limitations. | A reviewer can explain the user problem, intended decision, baseline, and how quality will be judged. |
| **2 — Prototype** | Hostable RAG workbench (**complete**) | Streamlit app; TXT/MD/PDF ingestion; chunking; BM25, dense-vector, and hybrid strategy switch; evidence inspection; grounded answer generation; deployment instructions. | App starts locally; users can change strategy and inspect ranked source chunks; no-key lexical demo still works. |
| **3 — Evaluate** | Offline benchmark and controlled comparisons (**complete: synthetic harness**) | Versioned labeled fixture; Recall@k, MRR, nDCG; per-query/slice reports; paired bootstrap intervals; latency and embedding-token accounting; top-k and RRF ablation controls; human answer/citation review rubric. | Harness is reproducible and compares selectable strategies when credentials are configured. The included synthetic run validates mechanics only; product-quality claims still require the production-data gate in `evaluation/README.md`. |
| **4 — Harden** | Production service architecture | Durable tenant-scoped document storage; asynchronous ingestion; managed index; auth/RBAC; deletion and retention; secrets management; rate limits; API contracts; CI/CD and infrastructure-as-code. | Threat model and privacy review complete; isolation, deletion, restart recovery, and load behavior verified in a staging deployment. |
| **5 — Observe** | Quality and reliability operations | Traces for retrieval and generation; feedback and failure taxonomy; alerts; dashboards; drift and cost monitoring; incident playbooks; canary/rollback. | SLOs and alert owners agreed; operators can trace a bad answer to documents, retrieval, prompt, or model version. |
| **6 — Improve** | Product iteration and stakeholder impact | User studies; query routing and/or reranking; new corpora and languages; measured experiments; accessibility and adoption improvements; decision memo. | A reviewed experiment shows a customer-relevant improvement without unacceptable latency, cost, or safety regression. |

## Prototype architecture

`Streamlit UI → parser/chunker → strategy adapter → ranked evidence → answer synthesis → citations and run metadata`

The prototype keeps data in Streamlit session state. BM25 is a local, deterministic baseline. Dense retrieval uses OpenAI embeddings and cosine similarity; hybrid retrieval uses reciprocal-rank fusion of BM25 and dense rankings. The strategy is selected on the dashboard per question. Phase 3's synthetic benchmark validates the comparison workflow, not a default strategy; a representative permissioned corpus and independently labeled questions are still required before making a quality claim. Phase 4 is the point to add persistent storage and multi-user controls.

## Recommended production target

- **UI:** Streamlit for an internal research console, or a web frontend over a versioned API for a customer-facing product.
- **API and jobs:** stateless Python service plus queue-backed ingestion workers.
- **Storage:** encrypted object storage for originals; metadata database with tenant and document ACLs; managed vector and lexical indexes.
- **Models:** provider adapter with pinned model identifiers, timeout/retry policy, token/cost budgets, and a no-answer path.
- **Operations:** OpenTelemetry traces, structured audit events, deployment health checks, backups, deletion workflows, and SLOs.

This is a target architecture, not a claim that the prototype already implements those controls.
