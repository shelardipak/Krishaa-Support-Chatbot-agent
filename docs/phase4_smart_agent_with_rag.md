# Phase 4: Add Knowledge & Retrieval
```
Coding: Required
Tools/Skills: Embeddings, semantic search, retrieval-augmented generation, vector store integration, retrieval-quality testing
```

## ✅ 1. Add product documentation retrieval
The app uses `app.retrieval.qdrant_client.QdrantClientAdapter` to embed user queries and retrieve similar document chunks from a Qdrant collection. The retrieved items include vendor, text, source file, page number, and optional image links.

## ✅ 2. Connect retrieval to the agent
The retrieved context is passed into `app.agent.response_builder.build_response`, which builds a grounded prompt and sends it to the LLM. If retrieval returns useful context, the answer is based on that documentation.

## ✅ 3. Compare responses with and without retrieval
Without retrieval, the agent may answer from general model knowledge and risk hallucination. With retrieval, the assistant is guided by actual Raychem, CharCoat, and Mennekes product documentation.

## ✅ 4. Handle missing relevant context
If no relevant documents are found, the app uses `EscalationTool` and returns a safe escalation message instead of hallucinating. Safety also checks product relevance and returns a redirection message when the query is off-topic.

## ✅ 5. Retrieval quality considerations
The Qdrant adapter can filter by vendor and score threshold, and it falls back to deterministic demo payloads only when remote retrieval is unavailable. This preserves the app experience during local testing while keeping production behavior grounded in Qdrant.
