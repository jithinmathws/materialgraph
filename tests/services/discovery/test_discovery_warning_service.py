from app.services.discovery.warning_service import DiscoveryWarningService


def test_warning_service_does_not_treat_n_as_present_in_na():
    service = DiscoveryWarningService()
    candidates = [{"formula": "NaFePO4", "pretty_formula": "NaFePO4"}]

    warnings = service.build_warnings(
        candidates=candidates,
        avoid_element=None,
        prefer_element="N",
        limit=5,
        total_candidate_count=1,
    )

    assert "No returned candidate contains the preferred element N." in warnings


def test_warning_service_recognizes_exact_na_membership():
    service = DiscoveryWarningService()
    candidates = [{"formula": "NaFePO4", "pretty_formula": "NaFePO4"}]

    warnings = service.build_warnings(
        candidates=candidates,
        avoid_element=None,
        prefer_element="Na",
        limit=5,
        total_candidate_count=1,
    )

    assert "No returned candidate contains the preferred element Na." not in warnings


def test_warning_service_does_not_treat_s_as_present_in_si():
    service = DiscoveryWarningService()
    candidates = [{"formula": "SiO2", "pretty_formula": None}]

    warnings = service.build_warnings(
        candidates=candidates,
        avoid_element="S",
        prefer_element=None,
        limit=5,
        total_candidate_count=1,
    )

    assert "All returned candidates still contain the avoided element S." not in warnings
