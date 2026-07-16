# Problem Framing

## Primary objective
Build a Krishaa Engineers product support chatbot that answers engineering product questions for Raychem, CharCoat, and Mennekes. The chatbot should be grounded in product documentation, safe for public support usage, and capable of capturing contact details for protected requests.

## Primary user personas
- Support agent or field engineer seeking product information
- Technical sales or service team member validating product compatibility
- Customer requesting drawings, datasheets, or installation manuals
- Internal team needing quick access to vendor-specific guidance

## Problem to solve
Technical product support teams currently spend time searching manuals, data sheets, and product notes for vendor-specific answers. The goal is to reduce search time and improve answer quality by using a retrieval-augmented chatbot that answers from Raychem, CharCoat, and Mennekes documentation and safely routes sensitive requests.

## Inputs
- User question describing a product need or issue
- Optional vendor filter
- Retrieval items from Qdrant including text, source file, page number, and image URLs

## Outputs
- A grounded support answer
- Reference links or document citations
- Escalation signal for unsupported or sensitive requests
- Contact-capture flow for protected document requests
- Stored feedback for product improvement

## Constraints
- Must avoid hallucinating unsupported product claims
- Must restrict answers to Raychem, CharCoat, and Mennekes
- Must handle safety and unsupported request types gracefully
- Must not expose raw embeddings or vector internals to users

## Success criteria
- Accurate product support answers
- Clear escalation for unsupported requests
- Functional contact-capture workflow for protected documents
- Feedback storage for later review
- Reliable local deployment with Gradio

## Example user questions
- "Which Raychem joint should I use for a medium voltage cable transition?"
- "Does CharCoat have a fireproof coating for steel structures?"
- "I need the Mennekes industrial plug datasheet."
- "Can you show me the installation guide for Raychem termination kits?"
- "What is the recommended cable accessory for a 24kV cable?"
