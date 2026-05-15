from dpwh_fsa_extractor.grammars.grammar_definitions import (
    G4_ACCEPTING,
    G4_DEAD,
    G4_OFFICE_NAMES,
    G4_START,
    G4_TERMINALS,
)

STATES = G4_ACCEPTING | {
    "q0", "q1", "q2", "q3", "q4", "q5", "q6", "q7", "q8", "q9", "q10", "q11",
    G4_DEAD,
}

INITIAL_STATE = G4_START
ACCEPTING_STATES = G4_ACCEPTING
DEAD_STATE = G4_DEAD

VALID_NAMES = G4_OFFICE_NAMES
VALID_ORDINALS = G4_TERMINALS["ordinal"]
VALID_ROMANS = G4_TERMINALS["roman"]
SPECIAL_REGIONS = G4_TERMINALS["special_region"]
DEO_FULL = "District Engineering Office"
DEO_ABBREV = "DEO"

TRANSITIONS = {
    ("q0", "n"): ("q1", 0),
    ("q0", "k"): ("q8", 0),
    ("q0", "g"): ("q11", 1),
    ("q0", "d"): (DEAD_STATE, 0),
    ("q0", "e"): (DEAD_STATE, 0),
    ("q0", "o"): (DEAD_STATE, 0),
    ("q0", "r"): (DEAD_STATE, 0),
    ("q0", "s"): (DEAD_STATE, 0),
    ("q1", "s"): ("q2", 0),
    ("q1", "n"): (DEAD_STATE, 0),
    ("q1", "k"): (DEAD_STATE, 0),
    ("q1", "d"): (DEAD_STATE, 0),
    ("q1", "e"): (DEAD_STATE, 0),
    ("q1", "o"): (DEAD_STATE, 0),
    ("q1", "r"): (DEAD_STATE, 0),
    ("q2", "d"): ("q3", 1),
    ("q2", "e"): ("q4", 1),
    ("q2", "o"): ("q5", 0),
    ("q2", "n"): (DEAD_STATE, 0),
    ("q2", "k"): (DEAD_STATE, 0),
    ("q2", "r"): (DEAD_STATE, 0),
    ("q2", "s"): (DEAD_STATE, 0),
    ("q5", "s"): ("q6", 0),
    ("q5", "n"): (DEAD_STATE, 0),
    ("q5", "k"): (DEAD_STATE, 0),
    ("q5", "d"): (DEAD_STATE, 0),
    ("q5", "e"): (DEAD_STATE, 0),
    ("q5", "o"): (DEAD_STATE, 0),
    ("q5", "r"): (DEAD_STATE, 0),
    ("q6", "d"): ("q7", 1),
    ("q6", "e"): ("q7", 1),
    ("q6", "n"): (DEAD_STATE, 0),
    ("q6", "k"): (DEAD_STATE, 0),
    ("q6", "o"): (DEAD_STATE, 0),
    ("q6", "r"): (DEAD_STATE, 0),
    ("q6", "s"): (DEAD_STATE, 0),
    ("q8", "s"): ("q9", 0),
    ("q8", "n"): (DEAD_STATE, 0),
    ("q8", "k"): (DEAD_STATE, 0),
    ("q8", "d"): (DEAD_STATE, 0),
    ("q8", "e"): (DEAD_STATE, 0),
    ("q8", "o"): (DEAD_STATE, 0),
    ("q8", "r"): (DEAD_STATE, 0),
    ("q9", "r"): ("q10", 1),
    ("q9", "n"): (DEAD_STATE, 0),
    ("q9", "k"): (DEAD_STATE, 0),
    ("q9", "d"): (DEAD_STATE, 0),
    ("q9", "e"): (DEAD_STATE, 0),
    ("q9", "o"): (DEAD_STATE, 0),
    ("q9", "s"): (DEAD_STATE, 0),
    (DEAD_STATE, "n"): (DEAD_STATE, 0),
    (DEAD_STATE, "k"): (DEAD_STATE, 0),
    (DEAD_STATE, "d"): (DEAD_STATE, 0),
    (DEAD_STATE, "e"): (DEAD_STATE, 0),
    (DEAD_STATE, "o"): (DEAD_STATE, 0),
    (DEAD_STATE, "r"): (DEAD_STATE, 0),
    (DEAD_STATE, "s"): (DEAD_STATE, 0),
    (DEAD_STATE, "g"): (DEAD_STATE, 0),
}


def _tokenize(office_string: str) -> list | None:
    s = office_string.strip()
    tokens = []

    multi_word = (
        sorted(VALID_NAMES, key=len, reverse=True)
        + [DEO_FULL]
        + sorted(VALID_ORDINALS, key=len, reverse=True)
        + sorted(VALID_ROMANS, key=len, reverse=True)
        + sorted(SPECIAL_REGIONS, key=len, reverse=True)
        + ["Region", DEO_ABBREV]
    )

    i = 0
    while i < len(s):
        if s[i] == " ":
            tokens.append(" ")
            i += 1
            continue

        matched_token = None
        for terminal in multi_word:
            end = i + len(terminal)
            if s[i:end] == terminal:
                if end == len(s) or s[end] == " ":
                    matched_token = terminal
                    i = end
                    break

        if matched_token is None:
            return None

        tokens.append(matched_token)

    return tokens if tokens else None


def _classify(token: str) -> str:
    if token == " ":
        return "s"
    if token in SPECIAL_REGIONS:
        return "g"
    if token == "Region":
        return "k"
    if token == DEO_FULL:
        return "d"
    if token == DEO_ABBREV:
        return "e"
    if token in VALID_ORDINALS:
        return "o"
    if token in VALID_ROMANS:
        return "r"
    if token in VALID_NAMES:
        return "n"
    return ""


def run_fsa(office_string: str) -> dict:
    office_string = office_string.strip()

    if not office_string:
        return {"matched": False, "value": office_string}

    tokens = _tokenize(office_string)

    if tokens is None:
        return {"matched": False, "value": office_string}

    current_state = INITIAL_STATE

    for token in tokens:
        symbol = _classify(token)

        if not symbol:
            return {"matched": False, "value": office_string}

        transition = TRANSITIONS.get((current_state, symbol))

        if transition is None:
            return {"matched": False, "value": office_string}

        next_state, _ = transition
        current_state = next_state

    matched = current_state in ACCEPTING_STATES
    return {"matched": matched, "value": office_string}
