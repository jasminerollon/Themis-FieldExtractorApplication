STATES = {
    'q0', 'q1', 'q2', 'q3', 'q4',
    'q5', 'q6', 'q7', 'q8', 'q9', 'q10', 'q_err'
}

ALPHABET = {'n', 'k', 'd', 'o', 'r', 's'}

INITIAL_STATE = 'q0'

ACCEPTING_STATES = {'q3', 'q4', 'q7', 'q10'}

VALID_NAMES = {
    'Abra', 'Agusan del Norte', 'Agusan del Sur', 'Aklan', 'Albay',
    'Antique', 'Apayao', 'Aurora', 'Bacolod City', 'Baguio', 'Bataan',
    'Batanes', 'Batangas', 'Benguet', 'Biliran', 'Bohol', 'Bukidnon',
    'Bulacan', 'Butuan City', 'Cagayan', 'Cagayan de Oro City',
    'Camarines Norte', 'Camarines Sur', 'Camiguin', 'Capiz',
    'Catanduanes', 'Cavite', 'Cebu', 'Cebu City',
    'Cordillera Administrative', 'Cotabato', 'Davao City',
    'Davao del Norte', 'Davao del Sur', 'Davao de Oro',
    'Davao Occidental', 'Davao Oriental', 'Dinagat Islands',
    'Eastern Samar', 'Guimaras', 'Ifugao', 'Isabela', 'Iligan City',
    'Ilocos Norte', 'Ilocos Sur', 'Iloilo', 'Iloilo City', 'Laguna',
    'Lanao del Norte', 'Las Pinyas-Muntinlupa', 'La Union', 'Leyte',
    'Lower Kalinga', 'Malabon-Navotas', 'Marinduque', 'Masbate',
    'Metro Manila', 'MIMAROPA', 'Mindoro Occidental', 'Mindoro Oriental',
    'Misamis Occidental', 'Misamis Oriental', 'Mountain Province',
    'National Capital', 'Negros Occidental', 'Negros Oriental',
    'North Manila', 'Northern Samar', 'Nueva Ecija', 'Nueva Vizcaya',
    'Palawan', 'Pampanga', 'Pangasinan', 'Quezon', 'Quezon City',
    'Quirino', 'Rizal', 'Romblon', 'Samar', 'Sarangani', 'Siquijor',
    'Sorsogon', 'South Cotabato', 'South Manila', 'Southern Mindoro',
    'Southern Leyte', 'Sultan Kudarat', 'Surigao del Norte',
    'Surigao del Sur', 'Tacloban City', 'Tarlac', 'Upper Kalinga',
    'Zambales', 'Zamboanga City', 'Zamboanga del Norte',
    'Zamboanga del Sur', 'Zamboanga Sibugay'
}

VALID_ORDINALS = {'1st', '2nd', '3rd', '4th', '5th', '6th', '7th'}

VALID_ROMANS = {
    'I', 'II', 'III', 'IV-A', 'IV-B', 'V', 'VI', 'VII',
    'VIII', 'IX', 'X', 'XI', 'XII', 'XIII'
}

# Output: 1 = accepting transition, 0 = non-accepting
TRANSITIONS = {
    ('q0',    'n'): ('q1',    0),
    ('q0',    'k'): ('q8',    0),
    ('q0',    'd'): ('q_err', 0),
    ('q0',    'o'): ('q_err', 0),
    ('q0',    'r'): ('q_err', 0),
    ('q0',    's'): ('q_err', 0),
    ('q1',    's'): ('q2',    0),
    ('q1',    'n'): ('q_err', 0),
    ('q1',    'k'): ('q_err', 0),
    ('q1',    'd'): ('q_err', 0),
    ('q1',    'o'): ('q_err', 0),
    ('q1',    'r'): ('q_err', 0),
    ('q2',    'k'): ('q3',    1),
    ('q2',    'd'): ('q4',    1),
    ('q2',    'o'): ('q5',    0),
    ('q2',    'n'): ('q_err', 0),
    ('q2',    'r'): ('q_err', 0),
    ('q2',    's'): ('q_err', 0),
    ('q5',    's'): ('q6',    0),
    ('q5',    'n'): ('q_err', 0),
    ('q5',    'k'): ('q_err', 0),
    ('q5',    'd'): ('q_err', 0),
    ('q5',    'o'): ('q_err', 0),
    ('q5',    'r'): ('q_err', 0),
    ('q6',    'd'): ('q7',    1),
    ('q6',    'n'): ('q_err', 0),
    ('q6',    'k'): ('q_err', 0),
    ('q6',    'o'): ('q_err', 0),
    ('q6',    'r'): ('q_err', 0),
    ('q6',    's'): ('q_err', 0),
    ('q8',    's'): ('q9',    0),
    ('q8',    'n'): ('q_err', 0),
    ('q8',    'k'): ('q_err', 0),
    ('q8',    'd'): ('q_err', 0),
    ('q8',    'o'): ('q_err', 0),
    ('q8',    'r'): ('q_err', 0),
    ('q9',    'r'): ('q10',   1),
    ('q9',    'n'): ('q_err', 0),
    ('q9',    'k'): ('q_err', 0),
    ('q9',    'd'): ('q_err', 0),
    ('q9',    'o'): ('q_err', 0),
    ('q9',    's'): ('q_err', 0),
    ('q_err', 'n'): ('q_err', 0),
    ('q_err', 'k'): ('q_err', 0),
    ('q_err', 'd'): ('q_err', 0),
    ('q_err', 'o'): ('q_err', 0),
    ('q_err', 'r'): ('q_err', 0),
    ('q_err', 's'): ('q_err', 0),
}


def _tokenize(office_string: str) -> list | None:
    s = office_string.strip()
    tokens = []

    multi_word = (
        sorted(VALID_NAMES,    key=len, reverse=True)
        + ['District Engineering Office']
        + sorted(VALID_ORDINALS, key=len, reverse=True)
        + sorted(VALID_ROMANS,   key=len, reverse=True)
        + ['Region']
    )

    i = 0
    while i < len(s):
        if s[i] == ' ':
            tokens.append(' ')
            i += 1
            continue

        matched_token = None
        for terminal in multi_word:
            end = i + len(terminal)
            if s[i:end] == terminal:
                if end == len(s) or s[end] == ' ':
                    matched_token = terminal
                    i = end
                    break

        if matched_token is None:
            return None

        tokens.append(matched_token)

    return tokens if tokens else None


def _classify(token: str) -> str:
    if token == ' ':
        return 's'
    if token == 'Region':
        return 'k'
    if token == 'District Engineering Office':
        return 'd'
    if token in VALID_ORDINALS:
        return 'o'
    if token in VALID_ROMANS:
        return 'r'
    if token in VALID_NAMES:
        return 'n'
    return ''


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