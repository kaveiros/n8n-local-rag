#!/usr/bin/env python3
"""Regenerate docs/index.html from workflows/rag.json (run after re-exporting the workflow)."""
import html, json, pathlib

root = pathlib.Path(__file__).resolve().parent.parent
wf = json.loads((root / "workflows" / "rag.json").read_text(encoding="utf-8"))
wf_attr = html.escape(json.dumps(wf, ensure_ascii=False, separators=(",", ":")), quote=True)

page = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>n8n Local RAG (Ollama + PGVector)</title>
  <style>
    body {{ font-family: system-ui, sans-serif; max-width: 1100px; margin: 2rem auto; padding: 0 1rem; line-height: 1.5; color: #222; }}
    h1 {{ margin-bottom: .25rem; }}
    .sub {{ color: #666; margin-top: 0; }}
    n8n-demo {{ display: block; margin: 1.5rem 0; }}
    code, pre {{ background: #f4f4f5; border-radius: 4px; }}
    code {{ padding: .1rem .3rem; }}
    pre {{ padding: .75rem; overflow-x: auto; }}
    a {{ color: #ea4b71; }}
  </style>
  <script src="https://cdn.jsdelivr.net/npm/@webcomponents/webcomponentsjs@2.0.0/webcomponents-loader.js"></script>
  <script src="https://www.unpkg.com/lit@2.0.0-rc.2/polyfill-support.js"></script>
  <script type="module" src="https://cdn.jsdelivr.net/npm/@n8n_io/n8n-demo-component/n8n-demo.bundled.js"></script>
</head>
<body>
  <h1>n8n Local RAG</h1>
  <p class="sub">PDF and text ingestion into PGVector, chat with Ollama. Fully local.</p>

  <n8n-demo workflow="{wf_attr}" frame="true" clicktointeract="true"></n8n-demo>

  <h2>Use it</h2>
  <p>In n8n: <em>Workflows → Import from URL</em>:</p>
  <pre>https://raw.githubusercontent.com/kaveiros/n8n-local-rag/master/workflows/rag.json</pre>
  <p>Setup, SQL schema and troubleshooting are in the
     <a href="https://github.com/kaveiros/n8n-local-rag">GitHub repository</a>.</p>
</body>
</html>
"""
(root / "docs" / "index.html").write_text(page, encoding="utf-8")
print("wrote docs/index.html")
