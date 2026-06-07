import re


ELEMENT_SYMBOL_PATTERN = re.compile(r"^[A-Z][a-z]?$")

def extract_elements(formula: str | None) -> set[str]:
    if not formula:
        return set()

    return set(re.findall(r"[A-Z][a-z]?", formula))


def contains_element(formula: str | None, element: str) -> bool:
    return element in extract_elements(formula)


def is_valid_element_symbol(element: str | None) -> bool:
    if element is None:
        return True

    return bool(ELEMENT_SYMBOL_PATTERN.match(element))