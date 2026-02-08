---
name: debugging-skill
description: Systematic debugging method that combines ReAct (Reason+Act), error spotting, ambiguity identification, multi-solution generation via ToT (Tree-of-Thoughts), evaluation & selection, and step-by-step implementation using an externalized CoT (Chain-of-Thought) style. Ensures self-consistency and reproducible fixes.
---

# Debugging Skill

## Purpose
Provide a repeatable, auditable process to identify, triage, and fix defects in code, configuration, or system behaviour. Use ReAct for interaction with the environment, ToT to generate multiple candidate solutions, CoT-style explicit steps for implementing the chosen fix, and self-consistency checks to validate and lock the change.

---

## Instructions

1. **ReAct loop (Reason → Act → Observe)**
   - *Reason*: Formulate a concise hypothesis about the fault (one-sentence problem statement).
   - *Act*: Execute a focused experiment (run a test, reproduce bug, add a log, run a traceroute).
   - *Observe*: Collect deterministic evidence (stack traces, logs, input/outputs, timings).
   - Repeat until root cause narrowed.

2. **Spot errors & reproduce**
   - Reproduce the issue with minimal steps and a deterministic dataset.
   - Capture exact error messages, stack traces, HTTP responses, SQL queries, environment variables.
   - If non-deterministic, add instrumentation to capture state at failure time (request id, timestamps, thread id).

3. **Find ambiguity & list assumptions**
   - Explicitly list what is *known* vs *unknown* (inputs, expected outputs, environment).
   - Convert ambiguous requirements into concrete checks (e.g., “What does valid payload look like?”).
   - If assumptions are invalidated, update hypothesis.

4. **Generate multiple candidate solutions (ToT)**
   - Produce 3–6 distinct candidate fixes. Each candidate must be described succinctly:
     - *What changes*: code/config/migration/test
     - *Why it would work*: brief justification
     - *Risk & rollback*: side effects and how to revert
     - *Complexity & effort estimate*: tiny / small / medium / large
   - Prefer orthogonal candidates (different root-cause directions), not minor variants.

5. **Evaluate candidates**
   - Define acceptance criteria and scoring rubric (example below).
   - Score each candidate against criteria: correctness, risk, time-to-verify, performance impact, long-term maintainability.
   - Select the highest-scoring candidate; if tied, prefer lower risk / faster verification.

6. **Implement step-by-step using externalized CoT**
   - Convert the chosen candidate into an explicit numbered implementation plan:
     1. Small change #1 (file, line range)
     2. Tests to add/update (unit/integration/e2e)
     3. Migration or data backfill steps (if any)
     4. Deployment steps (feature flag, canary)
     5. Monitoring/alerts to observe after deploy
     6. Rollback instructions
   - Execute each step and record results (pass/fail, logs). If a step fails, return to ReAct with updated evidence.

7. **Self-consistency & verification**
   - Run the original reproduction scenario and regression suite.
   - Add regression tests that codify the bug reproduction and fix.
   - Perform independent verification (peer review or automated cross-check).
   - Check for unintended side effects via smoke tests and load tests if applicable.
   - Document the final root cause, chosen fix rationale, and the tests added.

8. **Close the loop**
   - Merge with a clear commit message and changelog entry.
   - Tag release and ensure monitoring dashboards/alerts are in place.
   - If fix involved operational config, run post-mortem or short RCA note and update runbooks.

---

## Evaluation Rubric (example)

| Criterion                  | Weight |
|---------------------------:|-------:|
| Correctness (fixes root cause) | 40%  |
| Risk / Safety             | 20%   |
| Time-to-verify            | 15%   |
| Performance impact        | 10%   |
| Maintainability / clarity | 15%   |

Score each candidate 0–5 per criterion, compute weighted sum, pick highest.

---
