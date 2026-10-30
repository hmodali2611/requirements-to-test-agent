"""req2test generate stories/checkout.md --out out/"""

from __future__ import annotations

import argparse
from pathlib import Path

from .agent import generate_plan
from .exporters import feature_filename, to_csv, to_gherkin, to_traceability
from .llm import get_llm
from .parser import parse_stories


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="req2test", description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    gen = sub.add_parser("generate", help="Generate tests from a stories markdown file")
    gen.add_argument("stories", type=Path)
    gen.add_argument("--out", type=Path, default=Path("out"))
    gen.add_argument("--max-rounds", type=int, default=3)
    args = ap.parse_args(argv)

    llm = get_llm()
    stories = parse_stories(args.stories.read_text())
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "features").mkdir(exist_ok=True)

    plans = []
    for story in stories:
        plan = generate_plan(story, llm, args.max_rounds)
        plans.append(plan)
        (args.out / "features" / feature_filename(plan)).write_text(to_gherkin(plan))
        status = "all criteria covered" if not plan.gaps else f"gaps: {', '.join(plan.gaps)}"
        print(f"{story.id}: {len(plan.tests)} tests in {plan.llm_rounds} round(s), {status}")

    (args.out / "test-cases.csv").write_text(to_csv(plans))
    (args.out / "traceability.md").write_text(to_traceability(plans))
    print(f"Wrote {args.out}/features/, test-cases.csv and traceability.md (provider: {llm.name})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
