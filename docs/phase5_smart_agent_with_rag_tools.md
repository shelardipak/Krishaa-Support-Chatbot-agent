# Phase 5: Enable Tool Usage
```
Coding: Required
Tools/Skills: Tool/function abstraction, routing logic, guardrails, escalation handling, source formatting
```

## ✅ 1. Define the app tools
The codebase exposes lightweight tool abstractions:
- `ProductRetrievalTool` — returns retrieval items from Qdrant
- `EscalationTool` — handles unsupported or low-confidence cases
- `SourceFormatterTool` — converts retrieval metadata into display-ready references
- `route_tool()` — chooses escalation when safety fails or retrieval is missing

## ✅ 2. Implement tool routing
`app.agent.graph.RAGAgent.chat()` uses `route_tool()` to decide whether the request should escalate or proceed with retrieval. If the request is unsafe or no documents are found, the app escalates instead of generating an ungrounded answer.

## ✅ 3. Demonstrate correct use
Example flows:
- Supported question with retrieval: returns grounded answer and references
- Protected request detected: triggers contact capture and lead form
- Unsupported query: returns a safe redirect message for supported vendors only

## ✅ 4. Document failed or unsupported calls
The app does not attempt to call tools when safety fails. It also avoids relying on retrieval when the context is insufficient. This prevents repeated unhelpful loops and preserves a clear escalation path.

## ✅ 5. Add guardrails
Guardrails in this phase include:
- product relevance checking in `app.agent.safety.safety_check`
- escalation for unsupported request types
- safe fallback when no retrieval items are available
- source metadata formatting for references in the UI
