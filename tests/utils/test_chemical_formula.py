from app.utils.chemical_formula import contains_element, extract_elements


def test_extract_elements_from_simple_formula():
    assert extract_elements("LiFePO4") == {"Li", "Fe", "P", "O"}


def test_extract_elements_from_formula_with_parentheses():
    assert extract_elements("Na3Fe(PO4)2") == {"Na", "Fe", "P", "O"}


def test_contains_element_exact_match():
    assert contains_element("LiFePO4", "Li") is True
    assert contains_element("NaFePO4", "Li") is False


def test_contains_element_does_not_match_partial_symbol():
    assert contains_element("CaCO3", "C") is True
    assert contains_element("CaCO3", "Co") is False
    assert contains_element("CoO2", "Co") is True