# Engineering and Product Justification

The solution uses a small, modular RAG stack that fits free-tier and low-cost hosting constraints.

## Design decisions
- Use a retrieval-augmented generation pattern instead of fine-tuning.
  - Benefit: avoids expensive model tuning and keeps the product grounded in vendor documentation.
  - Result: answers can be traced to Raychem, CharCoat, and Mennekes source text.
- Separate concerns into clear layers:
  - `app.agent.graph` handles dialogue flow, question classification, and escalation.
  - `app.retrieval.qdrant_client` abstracts embedding and similarity search.
  - `app.agent.response_builder` centralizes prompt assembly and LLM answer generation.
  - `app.ui.gradio_app` keeps UI rendering and response formatting isolated from core logic.
- Use explicit prompt variants and guardrails rather than relying on a single monolithic prompt.
  - This supports safer handling of protected requests, product relevance checks, and structured response expectations.
- Keep memory and lead capture lightweight.
  - Memory stores only the current conversation turns and active contact-capture state.
  - No long-term personal data retention is implemented by default.

## Tradeoffs
- Cost vs. capability:
  - Choosing vector retrieval plus hosted OpenAI/LLM calls is cheaper and faster than on-premise large-model inference, but depends on external API availability and cost.
- Flexibility vs. safety:
  - Conservative escalation and contact-capture logic reduces hallucination risk, but may decline or escalate some user queries that could have been answered with more aggressive retrieval.
- Offline performance vs. rapid iteration:
  - The current architecture favors a hosted Gradio UI and external Qdrant/OpenAI dependencies rather than a fully offline offline-first desktop app.
  - This is acceptable for product support, but it means deployment readiness must include network, API, and vendor access assumptions.
- Simplicity vs. deep knowledge modeling:
  - By focusing on document retrieval and prompt engineering, the product can deliver useful answers quickly.
  - It does not currently model world knowledge beyond the retrieved product documentation.

## Safety approach
- Use a layered safety pipeline:
  - `detect_protected_request` identifies requests for drawings, datasheets, installation manuals, test reports, pricing, and similar protected content.
  - `safety_check` classifies non-product or policy-sensitive questions and redirects them safely.
- Enforce escalation for protected or unsupported requests.
  - These are handled by a lead capture flow rather than direct product answer generation.
- Ground responses in retrieved context.
  - When the agent answers product questions, it builds responses from retrieval hits and cites sources.
  - If retrieval is insufficient, the agent still avoids speculative claims and uses a conservative safe-response path.
- Keep UI output accountable:
  - Gradio response formatting includes source citations, image handling, and explicit fallback messaging for unsupported queries.

## Deployment assumptions
- The target environment provides:
  - Python 3.10+ and a working package install of `gradio`, `langchain`, `qdrant-client`, and associated dependencies.
  - Access to OpenAI or another LLM endpoint configured via environment variables.
  - Qdrant vector storage with the relevant product documents indexed.
- The UI is designed for lightweight hosting:
  - Suitable for Hugging Face Spaces, standard cloud VM, or local engineering demos.
  - Network access is required for LLM calls and optional Supabase/public document URLs.
- Operational expectations:
  - The app should be deployed behind a stable network and with logging enabled for lead capture and error handling.
  - Fallback behavior should be monitored: missing dependencies or unavailable APIs should surface clear diagnostics rather than hidden failures.
- Future production hardening:
  - Add explicit health checks for Qdrant and LLM service readiness.
  - Add telemetry for escalation volume, lead capture success, and retrieval relevance.
