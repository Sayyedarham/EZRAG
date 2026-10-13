# Data Scientist Intern alignment

The project is framed as a product investigation with an implementable prototype. These are portfolio evidence points; they do not claim measured impact before a benchmark or user study has run.

| Internship expectation | Project evidence | Next proof point |
|---|---|---|
| Formulate approaches using algorithms and data sources | The product brief defines BM25, embedding cosine similarity, and reciprocal-rank fusion; the Phase 3 runner compares strategies over labeled evidence chunks. | Run dense/hybrid with an approved API key and repeat on permissioned representative data. |
| Incorporate product functionality and customer perspective | The analyst workflow starts from a real task: find a supported answer and inspect the passages before acting. Method choices are exposed with short descriptions. | Observe representative analysts and revise the workflow from task friction. |
| Explore data, discover questions, and state applicability/limitations | The brief identifies exact-match, paraphrase, multi-source, unanswerable, stale-source, and long-document slices; it records supported formats and missing OCR/access controls. | Profile a permissioned corpus and report coverage, skew, and missing data before tuning. |
| Interpret, validate, monitor, and iterate | The synthetic baseline reports Recall@k, MRR, nDCG, per-query rankings, latency, and method-comparison intervals; later phases scope ongoing monitoring. | Produce representative-data paired comparisons and ongoing quality/cost dashboards. |
| Communicate actionable insights to stakeholders | Roadmap exit criteria and proposed pilot thresholds give product and engineering peers decision points. | Present an evidence-backed recommendation with tradeoffs and limitations after evaluation. |
| Participate in peer review and act on feedback | Experiment design includes double labeling, disagreement resolution, blind answer review, and error analysis before algorithm changes. | Maintain a review log and update the benchmark and design from reviewer feedback. |

## Suggested interview narrative

“I framed document Q&A as a product-quality question: which retrieval strategy helps analysts find supportable answers in their own corpus? I built a workbench with a lexical baseline, dense retrieval, and rank-fusion hybrid so a reviewer can inspect the same query's evidence. I added a reproducible synthetic benchmark and a BM25 baseline, while keeping the small fixture separate from claims about real users. My next step is to run the comparison on permissioned representative data and human-review answer grounding, latency, and cost before recommending a default.”

Replace this narrative with actual benchmark and user findings after phases 3 and 6; do not present proposed targets as achieved results.
