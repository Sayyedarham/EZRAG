# Browser BYOK edition

`web/` is a static, browser-only version of RAG Workbench. It has no backend, account system, analytics, cookies, or server-side key storage.

- It indexes TXT and Markdown files in the tab with local BM25 retrieval.
- A supplied OpenAI key stays in memory in that tab and is used only for a direct request to OpenAI when the visitor selects **Generate answer**.
- Closing/reloading the tab removes the key and documents. The site host never receives either.

## Publish it

Deploy the contents of this directory to Cloudflare Pages, Netlify, GitHub Pages, or any static-file host. On Cloudflare Pages, use `web` as the build output directory and no build command; `_headers` supplies the recommended security headers. No environment variables or secret configuration are needed.

For a local preview, run from the repository root:

```bash
python -m http.server 8080 --directory web
```

Then visit `http://localhost:8080`.

## BYOK trade-off

Browser BYOK is ideal for a public demo or individual use because the host never holds users' keys or documents. It is not a replacement for a managed production service with login, organization controls, persistent collections, PDFs, team sharing, or compliance controls. Use the root Streamlit/Docker app for the desktop/internal-workbench path.
