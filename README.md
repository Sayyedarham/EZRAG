# RAG Workbench

A hostable RAG workbench for document-grounded answers with inspectable BM25, dense-vector, and hybrid retrieval. It is packaged as a secure single-tenant internal application: uploaded content is deliberately held only in the browser's Streamlit session and is never written to disk by this app.

There are now two ways to use it:

- **Browser BYOK:** the static [browser edition](web/README.md) is publishable on any static host. Visitors supply their own OpenAI key; files and key remain in their tab.
- **Desktop/internal workbench:** the Streamlit/Docker app in this repository supports PDF, TXT, and Markdown plus BM25, dense, and hybrid retrieval. This is the current desktop version.

## What is production-ready here

- Docker image that runs as an unprivileged user, exposes port `8501`, and includes a liveness check at `/_stcore/health`.
- Explicit host-managed production configuration. Hosted deployments do **not** render a field for users to enter provider credentials.
- XSRF protection, CORS protection, upload/file/page/chunk limits, encrypted-PDF rejection, per-session query throttling, bounded upstream retries/timeouts, and safe production error messages.
- Grounded generation with visible source evidence and a no-evidence response instead of irrelevant BM25 passages.
- A GitHub Actions verification workflow and unit tests, plus the existing offline retrieval benchmark.

## Run locally

Requires Python 3.11+.

```bash
python -m venv .venv
# Windows: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
$env:OPENAI_API_KEY = "your-key" # PowerShell; optional for BM25-only use
streamlit run app.py
```

Local development allows entering an API key in the sidebar by default. For a production-like local run, set `APP_ENV=production` and provide `OPENAI_API_KEY` through the environment.

## Deploy with Docker

Build and run with secrets injected by your host (never bake a `.env` or secrets file into the image):

```bash
docker build -t rag-workbench .
docker run --rm -p 8501:8501 \
  -e APP_ENV=production \
  -e OPENAI_API_KEY="your-key" \
  rag-workbench
```

Open `http://localhost:8501`. Configure your platform load balancer to probe `GET /_stcore/health` on port `8501`. Terminate TLS at the load balancer, restrict ingress to the intended organization/network, store `OPENAI_API_KEY` in the platform secret manager, and pin a container image digest for releases. Streamlit Community Cloud is also supported for non-sensitive demos: add `OPENAI_API_KEY` as an app secret; the app reads it as a host-managed secret.

## Configuration

| Variable | Default | Purpose |
|---|---:|---|
| `APP_ENV` | `development` | `development`, `staging`, or `production`; production hides the key-entry field. |
| `OPENAI_API_KEY` | empty | Host-managed environment key for dense/hybrid retrieval and answer generation. Streamlit app secrets are also accepted. |
| `OPENAI_CHAT_MODEL` | `gpt-4o-mini` | Chat model identifier. |
| `OPENAI_EMBEDDING_MODEL` | `text-embedding-3-small` | Embedding model identifier. |
| `ALLOW_USER_API_KEYS` | true in development | Set `false` for every shared deployment. |
| `MAX_UPLOAD_MB` | `10` | Per-file upload cap. Keep this aligned with `.streamlit/config.toml`. |
| `MAX_UPLOAD_FILES` | `10` | Files accepted in one indexing action. |
| `MAX_PDF_PAGES` | `100` | PDF parsing cap. |
| `MAX_CHUNKS_PER_SESSION` | `2000` | Total in-memory index cap per browser session. |
| `MAX_QUERIES_PER_MINUTE` | `20` | Per-session upstream request guard. |

The host must configure a valid API key for dense/hybrid strategies and generated answers. BM25 retrieval remains usable without one.

## Verification

```bash
pytest -q
python evaluation/run_benchmark.py --methods BM25 --output-dir evaluation/results
```

See [the evaluation guide](evaluation/README.md) for benchmark limitations and [the roadmap](docs/ROADMAP.md) for the controls required before evolving this into a multi-tenant service.
