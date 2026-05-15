import re

STATES = {'q1', 'q2', 'q3', 'q4', 'q5', 'q6', 'q7', 'q8'}

ALPHABET = {'m', 's', 'd', 'c', 'y'}

INITIAL_STATE = 'q1'

ACCEPTING_STATES = {'q7'}

VALID_MONTHS = {
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
}

VALID_DAYS = {str(i) for i in range(1, 32)} | {f"{i:02d}" for i in range(1, 32)}

VALID_YEARS = {'2018', '2019', '2020', '2021', '2022', '2023', '2024', '2025'}

# Output: 1 = accepting transition, 0 = non-accepting
TRANSITIONS = {
    ('q1', 'm'): ('q2', 0),
    ('q1', 's'): ('q8', 0),
    ('q1', 'd'): ('q8', 0),
    ('q1', 'c'): ('q8', 0),
    ('q1', 'y'): ('q8', 0),
    ('q2', 's'): ('q3', 0),
    ('q2', 'm'): ('q8', 0),
    ('q2', 'd'): ('q8', 0),
    ('q2', 'c'): ('q8', 0),
    ('q2', 'y'): ('q8', 0),
    ('q3', 'd'): ('q4', 0),
    ('q3', 'm'): ('q8', 0),
    ('q3', 's'): ('q8', 0),
    ('q3', 'c'): ('q8', 0),
    ('q3', 'y'): ('q8', 0),
    ('q4', 'c'): ('q5', 0),
    ('q4', 'm'): ('q8', 0),
    ('q4', 's'): ('q8', 0),
    ('q4', 'd'): ('q8', 0),
    ('q4', 'y'): ('q8', 0),
    ('q5', 's'): ('q6', 0),
    ('q5', 'm'): ('q8', 0),
    ('q5', 'd'): ('q8', 0),
    ('q5', 'c'): ('q8', 0),
    ('q5', 'y'): ('q8', 0),
    ('q6', 'y'): ('q7', 1),
    ('q6', 'm'): ('q8', 0),
    ('q6', 's'): ('q8', 0),
    ('q6', 'd'): ('q8', 0),
    ('q6', 'c'): ('q8', 0),
    ('q7', 'm'): ('q8', 0),
    ('q7', 's'): ('q8', 0),
    ('q7', 'd'): ('q8', 0),
    ('q7', 'c'): ('q8', 0),
    ('q7', 'y'): ('q8', 0),
    ('q8', 'm'): ('q8', 0),
    ('q8', 's'): ('q8', 0),
    ('q8', 'd'): ('q8', 0),
    ('q8', 'c'): ('q8', 0),
    ('q8', 'y'): ('q8', 0),
}

def _tokenize(token_string: str) -> list | None:
    match = re.match(
        r'^([A-Za-z]+)(\s)(\d{1,2})(,)(\s)(\d{4})$',
        token_string
    )
    if not match:
        return None

    month, sp1, day, comma, sp2, year = match.groups()

    symbols = []

    symbols.append(('m', month))
    symbols.append(('s', sp1))
    symbols.append(('d', day))
    symbols.append(('c', comma))
    symbols.append(('s', sp2))
    symbols.append(('y', year))

    return symbols


def run_fsa(token_string: str) -> dict:
    token_string = token_string.strip()

    if not token_string:
        return {"matched": False, "value": ""}

    symbols = _tokenize(token_string)

    if symbols is None:
        return {"matched": False, "value": token_string}

    current_state = INITIAL_STATE

    for symbol_class, value in symbols:
        if symbol_class == 'm' and value not in VALID_MONTHS:
            return {"matched": False, "value": token_string}
        if symbol_class == 'd' and value not in VALID_DAYS:
            return {"matched": False, "value": token_string}
        if symbol_class == 'y' and value not in VALID_YEARS:
            return {"matched": False, "value": token_string}

        transition = TRANSITIONS.get((current_state, symbol_class))

        if transition is None:
            return {"matched": False, "value": token_string}

        next_state, _ = transition
        current_state = next_state

    matched = current_state in ACCEPTING_STATES
    return {"matched": matched, "value": token_string}