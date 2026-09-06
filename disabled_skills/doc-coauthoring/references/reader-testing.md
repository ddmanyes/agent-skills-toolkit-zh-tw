# Reader testing

Use this stage when the user accepted independent reader testing. Test the document's usability with a fresh reader, not the authoring conversation's hidden knowledge.

## Stage 3: Reader Testing

**Goal:** Test the document with a fresh reader agent (no context bleed) to verify it works for readers.

**Instructions to user:**
Explain that testing will now occur to see if the document actually works for readers. This catches blind spots - things that make sense to the authors but might confuse others.

### Testing Approach

**If access to sub-agents is available (e.g., in Codex):**

Perform the testing directly without user involvement.

### Step 1: Predict Reader Questions

Announce intention to predict what questions readers might ask when trying to discover this document.

Generate 5-10 questions that readers would realistically ask.

### Step 2: Test with Sub-Agent

Announce that these questions will be tested with a fresh reader agent instance (no context from this conversation).

Give a fresh sub-agent the document and the reader questions without the authoring conversation. A single bounded review may cover the set; separate reviewers are useful only when independent audiences or documents require them.

Summarize what the reader agent got right/wrong for each question.

### Step 3: Run Additional Checks

Announce additional checks will be performed.

Invoke sub-agent to check for ambiguity, false assumptions, contradictions.

Summarize any issues found.

### Step 4: Report and Fix

If issues found:
Report that the reader agent struggled with specific issues.

List the specific issues.

Indicate intention to fix these gaps.

Loop back to refinement for problematic sections.

---

**If no access to sub-agents (e.g., the current app web interface):**

Offer the user the following manual test. Until it is run, mark reader testing as pending and deliver the reviewable draft with that limitation. Do not claim an independent test from the authoring agent's own review.

### Step 1: Predict Reader Questions

Derive reader questions from the audience and purpose. Ask the user only when the intended readers or their needs remain unclear.

Generate 5-10 questions that readers would realistically ask.

### Step 2: Setup Testing

Provide testing instructions:
1. Open a fresh conversation in an available app, without the authoring history
2. Paste or share the document content (if using a shared doc platform with connectors enabled, provide the link)
3. Ask the reader agent the generated questions

For each question, instruct the reader agent to provide:
- The answer
- Whether anything was ambiguous or unclear
- What knowledge/context the doc assumes is already known

Check if the reader agent gives correct answers or misinterprets anything.

### Step 3: Additional Checks

Also ask the reader agent:
- "What in this doc might be ambiguous or unclear to readers?"
- "What knowledge or context does this doc assume readers already have?"
- "Are there any internal contradictions or inconsistencies?"

### Step 4: Iterate Based on Results

Ask what the reader agent got wrong or struggled with. Indicate intention to fix those gaps.

Loop back to refinement for any problematic sections.

---

### Exit Condition (Both Approaches)

Reader testing passes when answers to the selected questions are supported by the draft, key assumptions are explicit, and no material contradiction remains. Record the questions, results, and repaired gaps. If missing facts or unavailable tools prevent a pass, report the specific blocked cases; do not loop indefinitely.

## Final Review

When Reader Testing passes:
Announce the doc has passed the reader agent testing. Before completion:

1. Recommend they do a final read-through themselves - they own this document and are responsible for its quality
2. Suggest double-checking any facts, links, or technical details
3. Ask them to verify it achieves the impact they wanted

Deliver when the agreed document requirements and checks are complete. A further review is optional when the user requests it or an unresolved issue remains.

**If user wants final review, provide it. Otherwise:**
Announce document completion. Provide a few final tips:
- Include development context in an appendix only when it helps readers and the user authorizes sharing it; review for private information first
- Use appendices to provide depth without bloating the main doc
- Update the doc as feedback is received from real readers
