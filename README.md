# Krishaa Engineers Support Chatbot

A lightweight Gradio-based assistant for product support questions about Raychem, CharCoat, and Mennekes. The chatbot is built around Qdrant retrieval, OpenAI chat models, and safe escalation logic. It also includes a contact-capture flow for protected document and pricing requests.

## What this app does
- Answers engineering product support questions using retrieved documentation context
- Filters requests to supported vendors: Raychem, CharCoat, Mennekes
- Escalates unsupported or unsafe requests to human support
- Captures contact details before submitting protected document or pricing requests
- Stores feedback in `feedback.jsonl`
- Optionally resolves source links via Supabase-hosted document URLs

## Technology Stack

| Component | Technology |
|-----------|------------|
| Frontend UI | Gradio |
| Chat / Prompt Engine | LangChain (`ChatOpenAI`, `ChatPromptTemplate`) |
| LLM Provider | OpenAI |
| Retrieval | Qdrant (remote) with deterministic fallback |
| Embeddings | OpenAI `text-embedding-3-small` |
| Storage | SQLite + `feedback.jsonl` |
| Config | `python-dotenv` |
| Email Notification | SMTP via `app.notifications.email` |
| Local Workflow | Python 3.10+ |

## Execution Flow

1. User enters a question in the Gradio UI.
2. The app receives the query in `app/ui/gradio_app.py` and forwards it to `app.agent.graph.RAGAgent.chat()`.
3. The agent performs safety checks in `app.agent.safety.safety_check()`.
   - If the query is off-topic, the assistant returns a product-relevance redirect.
   - If the query matches protected request patterns, the app starts the contact capture flow.
4. If the request passes safety, the agent queries Qdrant via `app.retrieval.qdrant_client.QdrantClientAdapter.search()`.
5. The agent decides whether to answer from retrieval or escalate using `app.agent.tools.route_tool()`.
6. `app.agent.response_builder.build_response()` generates the final answer:
   - If retrieval context exists, the answer is grounded in documentation.
   - If no relevant context is available, the app returns a safe fallback or escalation message.
7. The response is sent back to the UI with optional source references and image URLs.
8. User feedback is stored in `app/feedback/feedback_store.py`.

## Run locally

1. Create and activate a Python environment.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file with required secrets.
4. Start the app:
   ```bash
   python app.py
   ```

## Phase documentation
- [Phase 1: Problem framing](./docs/phase1_problem_framing_document.md)
- [Phase 2: Baseline agent](./docs/phase2_baseline_agent.md)
- [Phase 3: Smart agent improvements](./docs/phase3_smart_agent.md)
- [Phase 4: Retrieval-augmented generation](./docs/phase4_smart_agent_with_rag.md)
- [Phase 5: Tool usage](./docs/phase5_smart_agent_with_rag_tools.md)
- [Phase 6: Planning, memory & context](./docs/phase6_planning_memory_context.md)
- [Phase 7: Adaptive behaviour](./docs/phase7_adaptive_behaviour.md)
- [Phase 8: Deployment readiness](./docs/phase8_deployment_readiness.md)
- [Phase 9: Evaluation & engineering review](./docs/phase9_evaluation_engineering_review.md)

## Key configuration
The app uses these environment variables:
- `OPENAI_API_KEY`
- `OPENAI_MODEL`
- `OPENAI_EMBEDDING_MODEL`
- `QDRANT_URL`
- `QDRANT_API_KEY`
- `QDRANT_COLLECTION`
- `QDRANT_VECTOR_NAME`
- `QDRANT_SCORE_THRESHOLD`
- `QDRANT_ALLOW_FALLBACK`
- `SUPABASE_URL`
- `SUPABASE_STORAGE_BUCKET`
- `SUPABASE_DOCUMENT_BUCKET`
- `SMTP_HOST`
- `SMTP_PORT`
- `SMTP_USERNAME`
- `SMTP_APP_PASSWORD`
- `SMTP_FROM_EMAIL`
- `LEAD_NOTIFICATION_EMAIL`
- `LANGSMITH_TRACING`
- `LANGSMITH_API_KEY`

## Notes
- The app is optimized for lightweight deployment and simple product-support workflows.
- When Qdrant is unavailable, deterministic fallback data preserves chatbot flow for demos.
- Feedback is stored locally in `feedback.jsonl` and does not directly feed back into the current prompt chain.
