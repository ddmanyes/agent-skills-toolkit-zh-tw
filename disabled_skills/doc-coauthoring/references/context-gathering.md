# Context gathering

Use this stage after the user accepts the structured collaboration workflow and the brief still has material gaps. Reuse already supplied answers.

## Stage 1: Context Gathering

**Goal:** Close the gap between what the user knows and what the authoring agent knows, enabling smart guidance later.

### Initial Questions

Extract the following from the supplied context first. Ask only about missing facts that change the document:

1. What type of document is this? (e.g., technical spec, decision doc, proposal)
2. Who's the primary audience?
3. What's the desired impact when someone reads this?
4. Is there a template or specific format to follow?
5. Any other constraints or context to know?

Inform them they can answer in shorthand or dump information however works best for them.

**If user provides a template or mentions a doc type:**
- Use the supplied template; ask for one only if its structure is necessary and no template is available
- If they provide a link to a shared document, use the appropriate integration to fetch it
- If they provide a file, read it

**If user mentions editing an existing shared document:**
- Use the appropriate integration to read the current state
- Check for images without alt-text
- If images lack alt-text, inspect them using available image tools and describe essential meaning when document accessibility is in scope. If image access is unavailable, identify which image needs content from the user. Do not assume all readers or tools have the same image capabilities.

### Info Dumping

Once initial questions are answered, encourage the user to dump all the context they have. Request information such as:
- Background on the project/problem
- Related team discussions or shared documents
- Why alternative solutions aren't being used
- Organizational context (team dynamics, past incidents, politics)
- Timeline pressures or constraints
- Technical architecture or dependencies
- Stakeholder concerns

Advise them not to worry about organizing it - just get it all out. Offer multiple ways to provide context:
- Info dump stream-of-consciousness
- Point to team channels or threads to read
- Link to shared documents

**If integrations are available** (e.g., Slack, Teams, Google Drive, SharePoint, or other MCP servers), mention that these can be used to pull in context directly.

**If a required integration is unavailable:** state the access limitation and use supplied files or excerpts. Request only the missing material needed to answer the document's questions; do not invent a product URL or setup path.

Inform them clarifying questions will be asked once they've done their initial dump.

**During context gathering:**

- If user mentions team channels or shared documents:
  - If integrations available: Inform them the content will be read now, then use the appropriate integration
  - If integrations not available: Explain the access limitation and ask for the required excerpt or accessible file.

- If entities or projects need clarification, read connected sources within the already authorized task scope. Ask before accessing unrelated sources or expanding scope.

- As user provides context, track what's being learned and what's still unclear

**Asking clarifying questions:**

When user signals they've done their initial dump (or after substantial context provided), ask clarifying questions to ensure understanding:

Ask the smallest useful set of questions based on material gaps. For a broad discovery session, 5–10 numbered questions can help; use fewer or none when the supplied context is sufficient.

Inform them they can use shorthand to answer (e.g., "1: yes, 2: see #channel, 3: no because backwards compat"), link to more docs, point to channels to read, or just keep info-dumping. Whatever's most efficient for them.

**Exit condition:**
This stage is complete when the audience, purpose, required structure, supported facts, key decision or proposal, and unresolved material questions are recorded. Proceed with the known content; mark gaps that need user input instead of inventing facts.

**Transition:**
Proceed to drafting when the recorded context supports it. If the user is still providing context, let them finish; ask only for a material unresolved decision.

If user wants to add more, let them. When ready, proceed to Stage 2.
