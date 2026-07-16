# Phase 8: Deployment Readiness
```
Coding: Required
Tools/Skills: packaging, environment configuration, local deployment, logging, graceful failure handling
```

## ✅ 1. Package for local deployment
The app runs as a Gradio application from `app.py`. It is configured via environment variables in `.env`, and dependencies are declared in `requirements.txt` and `pyproject.toml`.

## ✅ 2. Capture runtime context
The app includes logging via `app.logging_config` and traces user interactions. It also logs feedback events and can optionally support LangSmith tracing through environment configuration.

## ✅ 3. Graceful failure handling
The app handles common failure cases by:
- returning a safe escalation message when Qdrant retrieval fails
- falling back to deterministic demo payloads if remote Qdrant is unavailable and fallback is enabled
- validating contact form input before submission
- keeping the Gradio session alive on errors

## ✅ 4. Document assumptions
For a working deployment, configure:
- OpenAI API keys and model settings
- Qdrant collection and vector names
- Supabase storage settings for document URLs
- SMTP credentials for lead notification email
- `LEAD_NOTIFICATION_EMAIL` for the target recipient

## ✅ 5. Deploy locally
Start the app with:
```bash
python app.py
```
Use the `demo/chat-widget.html` sample if you want an embedded front-end experience.
