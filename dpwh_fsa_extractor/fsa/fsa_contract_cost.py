STATES = {'q1', 'q2', 'q3', 'q4', 'q5', 'q6', 'q7', 'q8', 'q9', 'q10', 'q11', 'q12'}

ALPHABET = {'n', 'c', 'd'}  # n = digit, c = comma, d = decimal point

INITIAL_STATE = 'q1'

ACCEPTING_STATES = {'q11'}

# Output: 1 = accepting transition, 0 = non-accepting
TRANSITIONS = {
    ('q1',  'n'): ('q2',  0),
    ('q1',  'c'): ('q12', 0),
    ('q1',  'd'): ('q12', 0),
    ('q2',  'c'): ('q3',  0),
    ('q2',  'n'): ('q4',  0),
    ('q2',  'd'): ('q12', 0),
    ('q3',  'n'): ('q6',  0),
    ('q3',  'c'): ('q12', 0),
    ('q3',  'd'): ('q12', 0),
    ('q4',  'c'): ('q3',  0),
    ('q4',  'n'): ('q5',  0),
    ('q4',  'd'): ('q12', 0),
    ('q5',  'c'): ('q3',  0),
    ('q5',  'n'): ('q12', 0),
    ('q5',  'd'): ('q12', 0),
    ('q6',  'n'): ('q7',  0),
    ('q6',  'c'): ('q12', 0),
    ('q6',  'd'): ('q12', 0),
    ('q7',  'n'): ('q8',  0),
    ('q7',  'c'): ('q12', 0),
    ('q7',  'd'): ('q12', 0),
    ('q8',  'c'): ('q3',  0),
    ('q8',  'd'): ('q9',  0),
    ('q8',  'n'): ('q12', 0),
    ('q9',  'n'): ('q10', 0),
    ('q9',  'c'): ('q12', 0),
    ('q9',  'd'): ('q12', 0),
    ('q10', 'n'): ('q11', 1),
    ('q10', 'c'): ('q12', 0),
    ('q10', 'd'): ('q12', 0),
    ('q11', 'n'): ('q12', 0),
    ('q11', 'c'): ('q12', 0),
    ('q11', 'd'): ('q12', 0),
    ('q12', 'n'): ('q12', 0),
    ('q12', 'c'): ('q12', 0),
    ('q12', 'd'): ('q12', 0),
}


def _classify(char: str) -> str:
    if char.isdigit():
        return 'n'
    if char == ',':
        return 'c'
    if char == '.':
        return 'd'
    return ''

def _strip_currency_prefix(token_string: str) -> str:
    """Remove peso symbols and currency codes; G2 expects bare comma-formatted amounts."""
    s = token_string.strip()
    for prefix in ("\u20b1", "₱", "PHP", "PhP", "php"):
        if s.startswith(prefix):
            s = s[len(prefix):].lstrip()
    return s


def run_fsa(token_string: str) -> dict:
    token_string = _strip_currency_prefix(token_string)
    current_state = INITIAL_STATE

    for char in token_string:
        symbol = _classify(char)

        if not symbol:
            return {"matched": False, "value": token_string}

        transition = TRANSITIONS.get((current_state, symbol))

        if transition is None:
            return {"matched": False, "value": token_string}

        next_state, _ = transition
        current_state = next_state

    matched = current_state in ACCEPTING_STATES
    return {"matched": matched, "value": token_string}