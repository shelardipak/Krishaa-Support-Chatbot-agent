# Phase 7: Adaptive Behaviour
```
Coding: Required
Tools/Skills: feedback capture, behavior adjustment, safety adaptation, user satisfaction signals
```

## ✅ 1. Store feedback
The app records chat feedback using `app.feedback.feedback_store.FeedbackStore`. Feedback is stored in `feedback.jsonl` with an answer identifier and user selection.

## ✅ 2. Use feedback operationally
While the current implementation does not yet feed feedback directly back into the LLM prompt, it does preserve user satisfaction data for future improvement. The stored feedback can be used to tune prompts, adjust retrieval thresholds, and prioritize bug fixes.

## ✅ 3. Demonstrate behavior differences
The product behavior already adapts by handling protected requests and safety checks differently from simple support queries:
- a generic product support question returns grounded documentation
- a protected drawings/pricing request opens the lead capture flow
- an off-topic request returns a redirect notice

## ✅ 4. Explain what changed and why
This phase clarifies that the app is not only a chat interface but also a product support workflow manager. It separates straightforward support from escalation-worthy requests, and it records feedback for future agent tuning.

## ✅ 5. Improve the safety/adaptation boundary
Key adaptive behaviors in code:
- `safety_check()` verifies if the query is product-relevant
- `detect_protected_request()` triggers lead capture for sensitive document types
- `EscalationTool` returns an explicit escalation path for unsupported or low-confidence cases
