# Evaluation Report

## Phase 2: Baseline agent limitations
The baseline agent uses deterministic rule-based responses. It is simple and inexpensive but it has clear limitations:
- It cannot truly understand nuanced product questions.
- It cannot tailor the answer to the retrieved context beyond a simple template.
- It may overgeneralize or produce generic guidance when a specific answer is needed.

## Phase 3: Prompt strategy improvements
The repository implements three prompt strategies:
- baseline: simple template-driven support.
- grounded_rag: retrieval-grounded answer with citations.
- safety_first: conservative answers for electrical or fire safety questions.

The default strategy is grounded_rag because it balances helpfulness, safety, and traceability.

## Expected vs actual behavior
- For supported product questions, the agent should provide a grounded answer and source references. This is achieved in the current implementation.
- For unsafe requests, the agent should refuse and escalate. This is achieved through the safety filter.
- For off-topic questions, the agent should redirect to product-support topics. This is achieved through the safety and relevance checks.

## Additional failure modes to watch
- Retrieval may be too generic if the Qdrant collection is weak or low-quality.
- The fallback adapter is deterministic and should be replaced with native Qdrant integration for real deployments.
- Image URLs must be treated as optional context and only included when relevant to the answer.
