STATES = {
    'q1', 'q2', 'q3', 'q4', 'q5', 'q6', 'q7',
    'q8', 'q9', 'q10', 'q11', 'q12', 'q13', 'q14', 'q15', 'q16'
}

ALPHABET = {'d', 'l'}

INITIAL_STATE = 'q1'

ACCEPTING_STATES = {'q8', 'q9', 'q14', 'q15'}

# Output: 1 = accepting transition, 0 = non-accepting transition
TRANSITIONS = {
    ('q1',  'd'): ('q2',  0),
    ('q1',  'l'): ('q16', 0),
    ('q2',  'd'): ('q3',  0),
    ('q2',  'l'): ('q16', 0),
    ('q3',  'd'): ('q16', 0),
    ('q3',  'l'): ('q4',  0),
    ('q4',  'd'): ('q5',  0),
    ('q4',  'l'): ('q10', 0),
    ('q5',  'd'): ('q6',  0),
    ('q5',  'l'): ('q16', 0),
    ('q6',  'd'): ('q7',  0),
    ('q6',  'l'): ('q16', 0),
    ('q7',  'd'): ('q8',  1),
    ('q7',  'l'): ('q16', 0),
    ('q8',  'd'): ('q9',  1),
    ('q8',  'l'): ('q16', 0),
    ('q9',  'd'): ('q16', 0),
    ('q9',  'l'): ('q16', 0),
    ('q10', 'd'): ('q11', 0),
    ('q10', 'l'): ('q16', 0),
    ('q11', 'd'): ('q12', 0),
    ('q11', 'l'): ('q16', 0),
    ('q12', 'd'): ('q13', 0),
    ('q12', 'l'): ('q16', 0),
    ('q13', 'd'): ('q14', 1),
    ('q13', 'l'): ('q16', 0),
    ('q14', 'd'): ('q15', 1),
    ('q14', 'l'): ('q16', 0),
    ('q15', 'd'): ('q16', 0),
    ('q15', 'l'): ('q16', 0),
    ('q16', 'd'): ('q16', 0),
    ('q16', 'l'): ('q16', 0),
}

def _classify(char: str) -> str:
    if char.isdigit():
        return 'd'
    if char.isalpha() and char.isupper():
        return 'l'
    return ''


def run_fsa(token_string: str) -> dict:
    token_string = token_string.strip()
    current_state = INITIAL_STATE

    for char in token_string:
        symbol = _classify(char)

        if symbol is None:
            return {"matched": False, "value": token_string}

        transition = TRANSITIONS.get((current_state, symbol))

        if transition is None:
            return {"matched": False, "value": token_string}

        next_state, _ = transition
        current_state = next_state

    matched = current_state in ACCEPTING_STATES
    return {"matched": matched, "value": token_string}