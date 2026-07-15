# Problem Framing

## Primary user persona
The primary user is a customer support or field engineering representative who needs quick, reliable answers about engineering products from Raychem, CharCoat, and Mennekes. They are usually working under time pressure and need context-aware answers that are safe, concise, and grounded in product documentation.

## Daily workflow
A typical interaction starts with a public support question such as “Which Raychem joint is suitable for my application?” or “What fire protection product from CharCoat should I consider?” The support rep then asks the chatbot for a grounded explanation, optional supporting images, and source references so they can continue the case without extensive manual research.

## Exact problem being solved
The chatbot provides a low-cost, retrieval-augmented support layer over an existing Qdrant vector index containing product documentation and related image metadata. It answers public questions using only retrieved context, avoids fabrication, and escalates unresolved or safety-sensitive cases.

## Inputs, outputs, constraints, and assumptions
- Inputs: natural-language user queries, optional vendor filter, retrieved Qdrant chunk metadata.
- Outputs: grounded answer text, source references, optional image URLs, escalation status, and trace identifiers.
- Constraints: no persistent chat history, no personal data storage in logs, lightweight CPU-friendly hosting, and no heavy local inference.
- Assumptions: Qdrant and Supabase data already exist, the collection is already populated, and the environment exposes the required API keys.

## Success criteria
- The chatbot answers relevant product support questions accurately and briefly.
- It cites source file and page number where available.
- It refuses unsafe or off-topic requests and escalates when needed.
- The app runs reliably on free-tier or low-cost hosting with a simple Gradio interface.

## Known failure cases and edge scenarios
- The retrieval layer returns weak or irrelevant chunks.
- Questions ask for non-public or policy-sensitive information.
- The user asks for dangerous electrical or fire safety advice beyond the documentation.
- The context is insufficient for a confident answer and the agent must escalate rather than hallucinate.
