---
name: prompt-techniques
description: Prompting techniques for improving the promptlab classify prompt (classify_v1.txt to classify_v2.txt) and for planning IMPROVEMENT.md iterations. Use this skill whenever editing any file in prompts/, planning a prompt iteration, explaining why a prompt change helped or hurt, or writing prompts for Claude Code that go into PROMPTS.md.
---

# Prompting techniques for promptlab

## Rules for every iteration
1. Change ONE thing per iteration, so the measured effect has one cause.
2. Write the prediction BEFORE running the harness.
3. Measure with the same suite, temperature, max_tokens, and runs as the baseline.
4. Keep regressions visible. Do not delete cases that got worse.
5. Few-shot examples must NOT be tickets from the test suite. Otherwise the
   improvement is not honest. Write new examples or hold some tickets out.
6. Record the change that did not help. The brief requires it.
7. Do not tune the prompt to quirks of stubmodel.py. A different model is
   used at judging; improvements should be general prompt quality.

## Fundamental techniques
| Technique | What it looks like | Likely effect |
|---|---|---|
| Role | "You are a support-ticket classifier." | More focused answers |
| Clear task | "Classify the ticket into exactly one category." | Fewer vague outputs |
| Allowed labels | List every category with a one-line definition | Fewer invalid or wrong labels |
| Output format | "Respond with only a JSON object: {\"category\": ...}. No code fences, no text before or after." | json_valid and not_contains pass more |
| Constraints | "If unsure, choose the closest category. Never refuse." | Fewer refusals, fewer empty outputs |
| Delimiters | Wrap the input: `<ticket>...</ticket>` | Model separates instruction from data |

## Advanced techniques
| Technique | What it looks like | Watch out for |
|---|---|---|
| Few-shot | 2–4 input → JSON examples covering tricky categories | Longer prompt, higher tokens_in |
| Edge-case rules | "Refund requests are billing, not account." | Too many rules can confuse |
| Chain-of-thought | "Think step by step, then answer." | Extra text breaks JSON and max_tokens; a likely "did not help" |
| Hidden reasoning field | `{"reasoning": "...", "category": "..."}` | tokens_out rises; may hit max_tokens → finish=length |
| Self-check | "Before answering, confirm the category is in the list." | May add preamble text |
| Prompt chaining (for Claude Code work) | spec → plan → code → tests as separate requests | More steps, better control |

## Suggested iteration order
1. Role + clear task
2. Allowed labels with definitions
3. Strict JSON output format
4. Few-shot examples (held out from the test set)
5. Chain-of-thought (test it; expect it may hurt)
6. Edge-case rules targeting the worst remaining regressed/failed cases

## Reading results
- Accuracy up, tokens up a lot: note the trade-off explicitly.
- Fewer fails but more flaky: the prompt is not stable yet; not a clear win.
- Any regressed case: explain it before keeping the change.

## Prompts for Claude Code (for PROMPTS.md)
A good request has: context (point at SPEC.md), one precise task, constraints
(stdlib only, which files may change), the expected output, and a self-check.
For each of the 5 prompts in PROMPTS.md record: what you asked, what came
back, what you changed, and why.
