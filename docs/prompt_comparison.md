# Prompt Comparison for Krishaa Support Chatbot

This document compares the prompt templates used by the Krishaa Engineers support chatbot.

| Prompt | Purpose | Behavior Focus | Key Instructions | Special Handling |
|---|---|---|---|---|
| `app/prompts/v1_zero_shot_prompt.txt` | Direct zero-shot support answer | Use only retrieved documentation | Answer from context; if insufficient, say what is missing and recommend support | No invented claims, pricing, or unsupported links |
| `app/prompts/v2_few_shots_prompt.txt` | Few-shot example-based support | Example-driven behavior | Provide real examples of product support and escalation | Demonstrates protected-doc sharing rules |
| `app/prompts/v3_role_bases_prompt.txt` | Role-based assistant definition | Define assistant identity and responsibilities | Specify role, scope, and escalation behavior | Escalate protected/pricing requests; redirect out-of-scope |
| `app/prompts/v4_structured_output_prompt.txt` | Classification output format | Return structured JSON intent | Output intent/confidence in JSON; handle support vs pricing/docs vs out-of-scope | When not classifying, answer directly using context |
| `app/prompts/v5_chain_of_thoughts_prompt.txt` | Reasoning-style response | Step-by-step analysis before final answer | Identify intent, decide action, then answer concisely | Separate reasoning from final response |
| `app/prompts/v7_guardrail_prompt_safety_escalation.txt` | Safety and escalation guardrails | Enforce restrictions and safe escalation | Refuse protected/pricing requests; ask for contact details | Strongly prohibit unsupported links/claims |
| `app/prompts/v8_context_injection_prompt_advanced.txt` | Context-grounded answer generation | Use provided retrieved context only | Extract context, answer directly, or say what is missing | Do not answer from own knowledge without support context |
| `app/prompts/v9_tool_agent_prompt.txt` | Tool routing and selection | Choose between direct answer and tool use | Decide if action/tool is needed, otherwise answer clearly | No invented tool outputs; safe fallback if unsure |
| `app/prompts/v10_planning_memory_prompt.txt` | Planning with memory/workflow | Memory-aware product support planning | Classify intent, choose grounded answer/escalation, summarize | Uses product retrieval/escalation/contact tools |
| `app/prompts/v11_adaptive_prompt.txt` | Adaptive behavior with feedback | Adjust style based on feedback while keeping safety | Adapt to feedback, use tools only when needed, stay grounded | Prioritize safe, document-grounded support |

## Usage

Use this table when you need to understand which prompt file is responsible for each type of response behavior in the Krishaa support chatbot.
