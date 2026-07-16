# Phase 2: Build a Basic Working Agent
```
Coding: Required
Tools/Skills: Python, CLI or notebook workflow, input/output handling, basic rules/templates, logging sample runs
```

## ✅ 1. Create a Python-based agent that accepts user input
The initial version accepts chat queries and evaluates whether they are relevant to supported product vendors. It applies simple rules to route questions into support, escalation, or safe refusal.

## ✅ 2. Implement basic response generation
The baseline logic includes:
- product relevance filtering based on Raychem/CharCoat/Mennekes keywords
- a fallback response for unsupported or unsafe questions
- a simple contact prompt for protected information requests

**Example baseline flow**
- User: "I need the CharCoat fireproof coating datasheet"
- Agent: "I can help with CharCoat products, but I need to confirm your request and capture contact details before providing protected documents."

- User: "What is the recommended Raychem termination for a 11 kV cable?"
- Agent: "I can answer product support questions for Raychem, CharCoat, and Mennekes. Please provide more details or ask a specific product question."

## ✅ 3. Demonstrate limitations of the baseline agent
The baseline agent shows these limitations:
- narrow keyword matching for product relevance
- no retrieval of actual product documentation
- no ability to ground answers in a knowledge base
- no multi-turn memory beyond a single request

## ✅ 4. Log sample interactions and responses
The app captures user feedback events and chat messages in the Gradio UI, while the baseline design can log interactions for later review. The repository includes `app/feedback/feedback_store.py` for persisting feedback to `feedback.jsonl`.

## ✅ 5. Explain why this version is insufficient
A rule-based baseline is not enough for real product support because:
- product requests must be answered using actual vendor documentation,
- user phrasing is varied and requires semantic retrieval,
- the app must escalate protected requests safely,
- support agents need references and source metadata.
