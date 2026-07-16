# Phase 3: Make the Agent Smarter
```
Coding: Required
Tools/Skills: LLM integration, prompt design, structured response generation, prompt comparisons, failure mode analysis
```

## ✅ 1. Integrate an LLM into the agent workflow
The smart agent uses `ChatOpenAI` and LangChain prompt templates from `app.agent.response_builder`. It combines user queries with retrieved context and safety checks to generate product support answers.

## ✅ 2. Design and test prompt strategies
Prompt strategies center around:
- explicit product-support role framing
- grounding responses in retrieved documentation
- asking the model to avoid making unsupported claims
- returning concise, safe answers

The repository uses `DEFAULT_PROMPT` from `app.agent.prompts` to shape answer style and safety.

## ✅ 3. Compare outputs across prompt variants
The smart agent improves over baseline by:
- using natural language reasoning instead of fixed templates
- generating answers with product-specific phrasing
- applying safety rules to unsupported queries
- including source references when available

## ✅ 4. Document improvements and new failure modes
Improvements:
- More accurate, conversational product support
- Better handling of vendor-specific requests
- Safer behavior on unsupported topics

Failure modes:
- LLM hallucinations without retrieval context
- partial answers when context is insufficient
- overconfident responses to out-of-scope questions

## ✅ 5. Select a default prompt strategy
The default prompt encourages the assistant to be concise, safe, grounded in product documentation, and to escalate when it cannot answer confidently. This is implemented in `app.agent.prompts.DEFAULT_PROMPT`.
