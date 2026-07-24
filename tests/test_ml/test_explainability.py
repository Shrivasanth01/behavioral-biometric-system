import pytest
from ml.explainability import Explainer
from ml.config import MLConfig


class TestExplainer:
    @pytest.fixture
    def explainer(self):
        return Explainer()

    def test_reason_generation_high_risk(self, explainer):
        risk_data = {
            "ml_score": 80,
            "rules_score": 70,
            "heuristic_score": 60,
            "overall_score": 78,
            "night_hours": True,
            "new_device": True,
            "vpn_active": True,
            "amount": 50000,
            "transaction_count_24h": 20,
        }
        reasons = explainer.explain(risk_data)
        assert len(reasons) >= 3
        assert all(isinstance(r, str) and len(r) > 0 for r in reasons)

    def test_reason_generation_low_risk(self, explainer):
        risk_data = {
            "ml_score": 5,
            "rules_score": 0,
            "heuristic_score": 2,
            "overall_score": 3,
            "amount": 50,
            "transaction_count_24h": 1,
            "night_hours": False,
            "new_device": False,
            "vpn_active": False,
        }
        reasons = explainer.explain(risk_data)
        assert isinstance(reasons, list)

    def test_feature_contributions(self, explainer):
        risk_data = {
            "ml_score": 90,
            "rules_score": 80,
            "heuristic_score": 70,
            "overall_score": 85,
            "night_hours": True,
            "new_device": True,
            "vpn_active": False,
            "amount": 100000,
            "transaction_count_24h": 30,
        }
        contributions = explainer.get_feature_contributions(risk_data)
        assert len(contributions) >= 3
        for feat, val in contributions.items():
            assert isinstance(feat, str)
            assert isinstance(val, float)

    def test_reason_consistency(self, explainer):
        data = {"ml_score": 75, "rules_score": 65, "heuristic_score": 55, "overall_score": 70,
                "night_hours": True, "new_device": True, "vpn_active": False,
                "amount": 75000, "transaction_count_24h": 10}
        r1 = explainer.explain(data)
        r2 = explainer.explain(data)
        assert r1 == r2

    def test_empty_risk_data(self, explainer):
        data = {"ml_score": 0, "rules_score": 0, "heuristic_score": 0, "overall_score": 0}
        reasons = explainer.explain(data)
        assert isinstance(reasons, list)
        assert len(reasons) == 0 or all(len(r) > 0 for r in reasons)

    def test_reason_templates_format(self, explainer):
        for template in explainer._reason_templates:
            assert "{direction}" in template or "{pct}" in template or "{baseline}" in template or "{value}" in template

    def test_feature_ranking(self, explainer):
        data = {"ml_score": 80, "rules_score": 70, "heuristic_score": 60, "overall_score": 74}
        contributions = explainer.get_feature_contributions(data)
        sorted_feats = sorted(contributions.items(), key=lambda x: -abs(x[1]))
        assert len(sorted_feats) >= 3

    def test_boundary_scores(self, explainer):
        for score in [0, 1, 25, 50, 75, 99, 100]:
            data = {"ml_score": score, "rules_score": score, "heuristic_score": score,
                    "overall_score": score}
            reasons = explainer.explain(data)
            assert isinstance(reasons, list)

    def test_reason_for_high_transaction(self, explainer):
        data = {"amount": 500000, "overall_score": 85, "ml_score": 80, "rules_score": 70,
                "heuristic_score": 90, "night_hours": True, "new_device": True, "vpn_active": True,
                "transaction_count_24h": 25}
        reasons = explainer.explain(data)
        assert any("amount" in r.lower() or "transaction" in r.lower() for r in reasons)

    def test_reason_for_night_hours(self, explainer):
        data = {"amount": 1000, "overall_score": 60, "ml_score": 50, "rules_score": 70,
                "heuristic_score": 30, "night_hours": True, "new_device": False, "vpn_active": False,
                "transaction_count_24h": 5}
        reasons = explainer.explain(data)
        assert any("night" in r.lower() or "hour" in r.lower() for r in reasons)
