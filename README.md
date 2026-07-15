# Engineering Products RAG Chatbot

A lightweight, production-oriented RAG chatbot for public support questions about engineering products from Raychem, CharCoat, and Mennekes. The app uses LangChain-style orchestration, a Qdrant-backed retrieval layer, Gradio for the user experience, and optional LangSmith tracing for observability.

## Features
- Product support Q&A grounded in retrieved Qdrant context
- Vendor filter: All, Raychem, CharCoat, Mennekes
- Image display when a retrieved image URL is relevant
- Anonymous in-session memory only
- Safety checks and escalation for unsupported or sensitive requests
- Feedback collection via thumbs up/down without storing personal data
- Contact capture before releasing drawings, data sheets, installation manuals, detailed test reports, or pricing
- Configurable SMTP notification for qualified technical-support requests

## Local setup
1. Create and activate a Python environment.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy the example environment file and fill in secrets:
   ```bash
   cp .env.example .env
   ```
4. Run the app:
   ```bash
   python app.py
   ```

## Hugging Face Spaces deployment
Add the following secrets in Hugging Face Spaces:
- OPENAI_API_KEY
- OPENAI_MODEL
- OPENAI_EMBEDDING_MODEL
- OPENAI_EMBEDDING_DIMENSIONS (only for collections created with a custom dimension)
- QDRANT_URL
- QDRANT_API_KEY
- QDRANT_COLLECTION
- QDRANT_VECTOR_NAME (only for named-vector collections)
- QDRANT_SCORE_THRESHOLD (optional minimum similarity score)
- QDRANT_ALLOW_FALLBACK (keep false outside tests/demos)
- LANGSMITH_TRACING
- LANGSMITH_API_KEY
- LANGSMITH_PROJECT
- SUPABASE_URL
- SUPABASE_STORAGE_BUCKET
- SUPABASE_DOCUMENT_BUCKET (public bucket containing the source PDFs)
- LEAD_NOTIFICATION_EMAIL (defaults to `shelar.dipak@gmail.com`)
- SMTP_HOST, SMTP_PORT, SMTP_USERNAME, SMTP_APP_PASSWORD, SMTP_FROM_EMAIL
- SMTP_USE_TLS and SMTP_USE_SSL

For a real deployment, ensure your Qdrant collection already contains payload fields such as vendor, product_name, source_file, source_path, page_number, chunk_type, text, and image_url. The app will use those values automatically when present. Upload source PDFs to `SUPABASE_DOCUMENT_BUCKET` while preserving their Qdrant `source_path`; grounded chatbot answers will then end with deduplicated clickable document references.

Protected document and pricing requests start a four-step contact flow. The app sends the completed request through SMTP before confirming follow-up. For Gmail SMTP, use `smtp.gmail.com`, port `587`, TLS enabled, your full Gmail address as `SMTP_USERNAME`, and the generated 16-character Google App Password as `SMTP_APP_PASSWORD`. Never enter the regular Google account password.

The repository includes Hugging Face-compatible metadata at the top of this README.

---
title: Engineering Products RAG Chatbot
sdk: gradio
app_file: app.py
---

## Testing
Run the test suite with:
```bash
pytest -q
```

## Website widget demo
With the chatbot running on port 7860, start the sample website in another terminal:
```bash
python -m http.server 8080 --directory demo
```
Then open `http://localhost:8080/chat-widget.html` and click the floating chat button.

For a deployed chatbot, replace the iframe's `data-chatbot-url` in `demo/chat-widget.html`
or preview a URL without editing the file:
```text
http://localhost:8080/chat-widget.html?chatbot=https://your-space.hf.space
```

## Notes and limitations
- The repository intentionally avoids a heavy local model and uses a lightweight retrieval-backed agent.
- The current implementation uses a deterministic fallback retrieval adapter so the repository remains runnable even when Qdrant credentials are unavailable.
- For production, swap the adapter to a native Qdrant client integration and wire in a real LangChain chat model.
