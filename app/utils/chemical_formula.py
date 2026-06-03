import re


def extract_elements(formula: str | None) -> set[str]:
    if not formula:
        return set()

    return set(re.findall(r"[A-Z][a-z]?", formula))


def contains_element(formula: str | None, element: str) -> bool:
    return element in extract_elements(formula)