import csv
import io

from req2test.agent import generate_plan
from req2test.exporters import feature_filename, to_csv, to_gherkin, to_traceability
from req2test.llm import MockLLM
from req2test.parser import parse_stories


def plans(sample_md):
    return [generate_plan(s, MockLLM()) for s in parse_stories(sample_md)]


def test_gherkin_has_tags_and_steps(sample_md):
    feature = to_gherkin(plans(sample_md)[0])
    assert feature.startswith("@SHOP-101\nFeature: Apply a promo code at checkout")
    assert "@SHOP-101-TC01 @P1 @functional @AC1" in feature
    assert feature.count("Scenario:") == 8
    assert "    Then " in feature


def test_csv_has_one_row_per_test(sample_md):
    ps = plans(sample_md)
    rows = list(csv.DictReader(io.StringIO(to_csv(ps))))
    assert len(rows) == sum(len(p.tests) for p in ps)
    assert rows[0]["Steps"].startswith("1. ")


def test_traceability_lists_every_criterion(sample_md):
    md = to_traceability(plans(sample_md))
    assert "NOT COVERED" not in md
    assert md.count("| AC") == 9


def test_feature_filename(sample_md):
    assert feature_filename(plans(sample_md)[0]) == "shop-101-apply-a-promo-code-at-checkout.feature"
