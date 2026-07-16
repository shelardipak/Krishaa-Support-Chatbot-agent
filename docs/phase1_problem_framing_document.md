# Phase 1: Understand the Problem & Define Success
```
Coding: Not Required (optional)
Tools/Skills: Problem framing, user persona definition, workflow mapping, requirements writing, success criteria, edge-case thinking, evaluation planning
```

## ✅ 1. Identify the primary personas and workflow
### Primary personas
- Technical support agent handling product questions
- Field engineer verifying vendor product compatibility
- Service representative requesting drawings, datasheets, or pricing

### Workflow
1. User asks a product question or requests documentation
2. Agent verifies if the request is for Raychem, CharCoat, or Mennekes
3. The assistant returns a grounded answer or routes the request for human support
4. Protected document requests require contact capture before fulfillment

## ✅ 2. Define the problem
Technical support teams lack a fast, grounded way to answer product questions across Raychem, CharCoat, and Mennekes documentation. They need a lightweight support assistant that:
- returns answers grounded in real product documentation,
- avoids fabricated recommendations,
- escalates unsupported or safety-sensitive requests,
- captures contact details for drawings and pricing requests.

## ✅ 3. Inputs, outputs, constraints, assumptions
**Inputs**
- Natural language user query
- Optional vendor filter
- Retrieved Qdrant knowledge chunks

**Outputs**
- Grounded answer text
- Reference metadata for product documentation
- Escalation or follow-up action when needed
- Contact capture prompt for protected requests

**Constraints**
- Only support Raychem, CharCoat, Mennekes topics
- Must not answer unsafe or non-product requests directly
- Must use retrieved documentation context when available

**Assumptions**
- The Qdrant collection is populated with product documentation chunks
- Users can ask product support and documentation requests in plain language
- Email notification and SMTP configuration are available for lead capture flow

## ✅ 4. Example user questions
- "Which Raychem termination kit is best for a 33 kV cable?"
- "I need the CharCoat TDS for fireproof coating."
- "Can you give me the installation guide for a Mennekes socket?"
- "My product compatibility question is about Raychem cable accessories."
- "What drawings and pricing information are available for a Raychem joint?"

## ✅ 5. Success criteria
- Answers are grounded in product documentation
- Product relevance checks prevent off-topic completion
- Protected documents trigger contact capture
- Feedback is collected from users
- The app runs successfully in Gradio

## ✅ 6. Known failure cases
- User asks for unsupported products or general electrical safety advice
- Retrieval returns no relevant context and the agent hallucinates
- Protected document requests are not handled with contact capture
- Qdrant is unavailable and fallback behavior is not enabled
