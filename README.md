# MATACS-TH-2026-02: AI Proposal Triage Design

- **Name:** Sanjna
- **Reference:** MATACS-TH-2026-02
- **Time actually spent: 1 hour

## Files

| File | What it is |
|---|---|
| [WRITEUP.md](WRITEUP.md) | Answers to the five questions (under 1,000 words) |
| [diagram/process-flow.png](diagram/process-flow.png) | Flow from upload to ranked output: AI steps, rule steps, human checkpoints |
| [PROMPTS.md](PROMPTS.md) | The two prompts I would send (extraction, and reason sentence) |
| [ranking.json](ranking.json) | Expected ranking of proposals A to E |
| [prototype/](prototype/) | Optional: small script that applies the scoring rules (`python prototype/score.py`) |

## How I used AI tools

I used Claude to help me draft the whole submission: the process-flow diagram, the write-up, the prompts, the ranking and the small scoring script. I checked the sample ranking by running the script (`python prototype/score.py`) and compared the output with `ranking.json` and the write-up.

**Where I disagreed with or corrected the AI:** Claude's first draft of the write-up said proposal B would outscore E if the mandatory checks were skipped. When the script was run, B scored 61.9 and E scored 62.4, so the claim was wrong. The sentence was corrected to say B would score almost level with E, and that it is out only because it fails the mandatory licence check.
