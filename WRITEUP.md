# Write-up: MATACS-TH-2026-02

**Core idea:** AI reads the messy documents; plain code makes every decision. The AI only turns
PDF text into checked facts. Pass/fail, scoring and ranking are formulas driven by the admin's
criteria. A person reviews flags and makes the award.

## What my design gives for the sample set

| Proposal | Status | Score | Why |
|---|---|---|---|
| A | Ranked 1 | 74.7 | Most experience, full team plan, 12 weeks, within budget |
| E | Ranked 2 | 62.4 | Best warranty and monitoring; fewer installs, a bit pricier |
| D | Flagged | (59.9 provisional) | No completion time given, so the 16-week limit cannot be confirmed |
| C | Flagged | (53.6 provisional) | Hidden text tells automated reviewers to rank it first |
| B | Ineligible | n/a | Licence is not held by the bidder (subcontractor to be confirmed) |

Assumptions: "last 5 years" means counted as stated (2021 onward); C says "since 2020", so its
count may be too high and is marked uncertain. A missing completion time scores 0 and, because
the project has a hard 16-week limit, the proposal is flagged rather than ranked. B is cheapest and
would score 61.9 on paper, almost level with E, but mandatory criteria come first, so it is out. The scoring formulas are in `prototype/criteria.json`.

## 1. AI vs. rules

**AI (3 jobs):** (a) extract facts from each proposal with an exact supporting quote; (b) report
sentences that look like instructions to an AI; (c) write a one-line plain-English reason from
numbers the code already computed.

**Plain code:** PDF to text, checking the AI output, mandatory pass/fail, flags, all scoring
maths, ranking and tie-breaks, versioning and logging.

**Why the line is there:** AI is good at reading varied wording ("a six-person certified crew").
It is poor at being exact and repeatable, and it can be talked into things by text in a document.
Pass/fail and arithmetic are better as code: same input, same answer, and a reviewer can check
them. The AI never sees the weights and never outputs a score or rank.

## 2. Consistency and explainability

- Scores come from formulas applied to extracted facts, so identical facts always give identical
  scores. The only variable part is extraction.
- To control that: temperature 0, pinned model and prompt versions, strict JSON output, and each
  extraction is saved against the file's hash. Re-ranking reuses saved extractions, so ranking the
  same files twice gives the same result. A fresh re-extraction might word things differently, so
  I run extraction twice and flag any field where the runs disagree.
- Every extracted value must carry a quote that actually appears in the PDF text (checked by code).
- The reviewer sees, per proposal: each criterion, the extracted value, the quote, the points
  earned and the weight, plus a one-line reason. Close scores (within about 3 points) are shown as
  a near-tie rather than a firm order.

## 3. Human in the loop

- **Flags:** a person clears, corrects, asks for clarification, or excludes (D and C here).
- **Ineligible:** shown with the reason; the reviewer can challenge it, for example if "subcontractor"
  wording was misread.
- **Overrides:** the reviewer can edit an extracted value (shown next to the PDF page) or move a
  proposal, but must type a reason.
- **Award:** only a person decides. The tool shows a suggestion, not an award button.
- **Audit log:** uploaded file hashes, criteria version, prompt version, model name, raw AI
  output, extracted values, flags, scores, every human edit (who, when, before and after, why),
  and the final decision with its reason.

## 4. Changing criteria

- Criteria are stored as versions. Each score records the version used and is never overwritten.
- When an admin edits weights or criteria, a new version is created (weights must total 100).
  Old results stay readable as "scored under v1".
- Re-scoring is cheap because extracted facts are stored separately: formulas run again with no
  AI call. If a new criterion needs a fact that was not extracted, only that extraction is rerun.
- The reviewer sees "criteria changed since scoring" and must re-score the whole batch before a
  final decision, so proposals scored under different versions are never ranked together. The
  admin's edit is itself logged.

## 5. Risks and safeguards

| Risk | Safeguard |
|---|---|
| Wrong extraction | Quote must exist in the text; range checks; two runs must agree; reviewer sees the quote beside the value |
| Made-up facts | Rule: missing or vague means null, never guessed. Null scores 0 and is flagged. Unverifiable quote is rejected |
| Manipulation (C) | Proposal text is treated as data. The AI cannot change scores because code scores. Keyword scan plus AI report both flag it. Flagged proposals are held for a human; the injected text has no effect on any score |
| Bias | Scored only on admin criteria. Company names are not used in scoring. Poorly formatted or scanned PDFs get OCR and a human check rather than silent zeros. Overrides are reviewed periodically for patterns |
| Vague bids that look fine | Missing facts score 0, so vagueness cannot win (D) |
| Cost | One extraction per proposal (cached), a small model is enough, page limits, re-scoring is free |
| Over-trusting the AI | Output is labelled a suggestion, near-ties are shown, a human makes the award |
| Data privacy | Only approved providers, no personal data beyond business contact details, logs access-controlled |
