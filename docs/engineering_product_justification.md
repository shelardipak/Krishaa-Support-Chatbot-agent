# Engineering and Product Justification

The solution uses a small, modular RAG stack that fits free-tier and low-cost hosting constraints. The primary reasons for this architecture are:
- LangChain provides a clean orchestration layer for prompts, tools, and future LLM integration.
- Gradio offers a quick path to a polished UI that is simple to deploy on Hugging Face Spaces.
- A retrieval layer over Qdrant keeps the app cost-effective because it avoids fine-tuning or large local inference.
- The design preserves safety through explicit guardrails, escalation, and a conservative response policy.
- The feedback store is lightweight and can later be reused to improve retrieval and prompts without introducing persistent user history.
