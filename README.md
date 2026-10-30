# Requirements-to-Test Agent

[![CI](https://github.com/hmodali2611/requirements-to-test-agent/actions/workflows/ci.yml/badge.svg)](https://github.com/hmodali2611/requirements-to-test-agent/actions/workflows/ci.yml)

An LLM agent that reads user stories and acceptance criteria and produces **prioritized, traceable test cases**: Gherkin `.feature` files, a CSV ready for TestRail / Xray / Zephyr import, and a traceability matrix that shows every criterion is covered.

```text
$ req2test generate stories/checkout.md
SHOP-101: 8 tests in 2 round(s), all criteria covered
SHOP-102: 8 tests in 2 round(s), all criteria covered
Wrote out/features/, test-cases.csv and traceability.md
```

## Why an agent, not a single prompt

A single prompt usually returns happy-path tests and quietly skips the expired coupon, the 51st wishlist item, and the Android-to-web sync. This tool reviews the model's work with **deterministic coverage rules** and sends back only what is missing:

```text
story ─▶ draft tests (LLM) ─▶ validate (Pydantic) ─▶ review coverage (rules) ─┐
             ▲                                                                 │
             └────────────── "GAPS: negative AC2, boundary AC5" ◀──────────────┘   up to --max-rounds
```

The review checks that each acceptance criterion has:

| Rule | Triggered by wording like | Requires |
| --- | --- | --- |
| Coverage | every criterion | at least one test |
| Negative path | expired, invalid, guest, only one, full, not | a `negative` test |
| Boundary | at most 20 characters, max 50 items | a `boundary` test at the limit and one past it |
| Cross-platform | iOS, Android, web | a `cross_platform` test |

Invalid model output (missing steps, unknown criterion ids, wrong enum values) is rejected by the Pydantic schema and never reaches the output. Anything still uncovered after the last round is reported as an open gap, never hidden.

## Output

See [`examples/sample-output/`](examples/sample-output/) for a full run on [`stories/checkout.md`](stories/checkout.md).

```gherkin
@SHOP-101-TC07 @P2 @boundary @AC5
Scenario: Boundary: AC5 at 20 and 21
  Given Data set up to reach the limit of 20
  When Enter or add exactly 20
  And Verify it is accepted
  And Enter or add 21
  And Verify it is rejected with the documented message
  Then 20 is accepted and 21 is rejected
```

The bundled sample output comes from the offline **mock** model, so its steps are templated. With a real model (`LLM_PROVIDER=anthropic` or `openai`) the steps and expected results are specific to the story.

## Quick start

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest -q                                     # 11 tests
req2test generate stories/checkout.md --out out

# with a real model
export LLM_PROVIDER=anthropic ANTHROPIC_API_KEY=...
req2test generate stories/checkout.md --out out
```

Story format (works with text copied from Jira):

```markdown
# Story: SHOP-101 Apply a promo code at checkout
As a shopper I want to apply a promo code so that I pay the discounted price

## Acceptance criteria
- AC1: A valid, active promo code reduces the order total by its discount percentage
- AC2: An expired promo code shows "This code has expired" and the total is unchanged
```

## Project layout

| Path | What it is |
| --- | --- |
| `src/req2test/agent.py` | Draft → validate → review → fill-gaps loop |
| `src/req2test/models.py` | Pydantic schema for stories and test cases |
| `src/req2test/parser.py` | Markdown story parser |
| `src/req2test/exporters.py` | Gherkin, CSV and traceability output |
| `src/req2test/llm.py` | Anthropic / OpenAI providers (standard library HTTP) and the offline mock |
| `tests/` | Parser, agent loop (including a deliberately bad model), exporters |

## Tech

Python · Pydantic · LLM APIs (Anthropic, OpenAI) · Gherkin / Cucumber · pytest · GitHub Actions

## Run with a real model in CI

Add an `ANTHROPIC_API_KEY` repository secret, then run the **Real LLM generation** workflow from the Actions tab. The generated features, CSV and traceability matrix are uploaded as an artifact.

## License

MIT
