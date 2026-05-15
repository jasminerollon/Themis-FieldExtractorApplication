"""
Formal grammar and DFA specifications for G1–G4 (CS 223 DPWH FSA Extractor).

Right-linear grammars and transition tables follow the project paper.
FSAs in dpwh_fsa_extractor/fsa/ implement these definitions at runtime.
"""

# ---------------------------------------------------------------------------
# G1: Contract ID — dd(l | ll)(dddd | ddddd)
# ---------------------------------------------------------------------------
G1_STATES = {
    "q1", "q2", "q3", "q4", "q5", "q6", "q7", "q8", "q9",
    "q10", "q11", "q12", "q13", "q14", "q15", "q16",
}
G1_START = "q1"
G1_ACCEPTING = {"q8", "q9", "q14", "q15"}
G1_DEAD = "q16"

G1_TERMINALS = {
    "digit": set("0123456789"),
    "letter": set("ABCDEFGHIJKLMNOPQRSTUVWXYZ"),
}

G1_TRANSITIONS = {
    ("q1", "digit"): ["q2"],
    ("q2", "digit"): ["q3"],
    ("q3", "letter"): ["q4"],
    ("q4", "digit"): ["q5"],
    ("q4", "letter"): ["q10"],
    ("q5", "digit"): ["q6"],
    ("q6", "digit"): ["q7"],
    ("q7", "digit"): ["q8"],
    ("q8", "digit"): ["q9"],
    ("q10", "digit"): ["q11"],
    ("q11", "digit"): ["q12"],
    ("q12", "digit"): ["q13"],
    ("q13", "digit"): ["q14"],
    ("q14", "digit"): ["q15"],
}

# ---------------------------------------------------------------------------
# G2: Contract Cost — (n | nn | nnn)(,nnn)*(.nn)
# ---------------------------------------------------------------------------
G2_STATES = {
    "q1", "q2", "q3", "q4", "q5", "q6", "q7", "q8", "q9", "q10", "q11", "q12",
}
G2_START = "q1"
G2_ACCEPTING = {"q11"}
G2_DEAD = "q12"

G2_TERMINALS = {
    "digit": set("0123456789"),
    "comma": {","},
    "dot": {"."},
}

G2_TRANSITIONS = {
    ("q1", "digit"): ["q2"],
    ("q2", "comma"): ["q3"],
    ("q2", "digit"): ["q4"],
    ("q3", "digit"): ["q6"],
    ("q4", "comma"): ["q3"],
    ("q4", "digit"): ["q5"],
    ("q5", "comma"): ["q3"],
    ("q6", "digit"): ["q7"],
    ("q7", "digit"): ["q8"],
    ("q8", "comma"): ["q3"],
    ("q8", "dot"): ["q9"],
    ("q9", "digit"): ["q10"],
    ("q10", "digit"): ["q11"],
}

# ---------------------------------------------------------------------------
# G3: Contract Dates — m s d c s y  (long-form administrative dates)
# ---------------------------------------------------------------------------
G3_STATES = {"q1", "q2", "q3", "q4", "q5", "q6", "q7", "q8"}
G3_START = "q1"
G3_ACCEPTING = {"q7"}
G3_DEAD = "q8"

G3_TERMINALS = {
    "month": {
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December",
    },
    "space": {" "},
    "day": {str(i) for i in range(1, 32)} | {f"{i:02d}" for i in range(1, 32)},
    "comma": {","},
    "year": {"2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025"},
}

G3_TRANSITIONS = {
    ("q1", "month"): ["q2"],
    ("q2", "space"): ["q3"],
    ("q3", "day"): ["q4"],
    ("q4", "comma"): ["q5"],
    ("q5", "space"): ["q6"],
    ("q6", "year"): ["q7"],
}

# ---------------------------------------------------------------------------
# G4: Implementing Office — word-token level
# Production rules (paper):
#   Σ → name A | Region C | NCR | CAR | NIR
#   A → "District Engineering Office" | ord B | DEO
#   B → DEO
#   C → rom
# ---------------------------------------------------------------------------
G4_STATES = {
    "q0", "q1", "q2", "q3", "q4", "q5", "q6", "q7", "q8", "q9", "q10", "q11",
}
G4_START = "q0"
G4_ACCEPTING = {"q3", "q4", "q7", "q10", "q11"}
G4_DEAD = "q_err"

G4_OFFICE_NAMES = {
    "Abra", "Agusan del Norte", "Agusan del Sur", "Aklan", "Albay",
    "Antique", "Apayao", "Aurora", "Bacolod City", "Baguio", "Bataan",
    "Batanes", "Batangas", "Benguet", "Biliran", "Bohol", "Bukidnon",
    "Bulacan", "Butuan City", "Cagayan", "Cagayan de Oro City",
    "Camarines Norte", "Camarines Sur", "Camiguin", "Capiz",
    "Catanduanes", "Cavite", "Cebu", "Cebu City",
    "Cordillera Administrative", "Cotabato", "Davao City",
    "Davao del Norte", "Davao del Sur", "Davao de Oro",
    "Davao Occidental", "Davao Oriental", "Dinagat Islands",
    "Eastern Samar", "Guimaras", "Ifugao", "Isabela", "Iligan City",
    "Ilocos Norte", "Ilocos Sur", "Iloilo", "Iloilo City", "Laguna",
    "Lanao del Norte", "Las Piñas-Muntinlupa", "La Union", "Leyte",
    "Lower Kalinga", "Malabon-Navotas", "Marinduque", "Masbate",
    "Metro Manila", "MIMAROPA", "Mindoro Occidental", "Mindoro Oriental",
    "Misamis Occidental", "Misamis Oriental", "Mountain Province",
    "National Capital", "Negros Occidental", "Negros Oriental",
    "North Manila", "Northern Samar", "Nueva Ecija", "Nueva Vizcaya",
    "Palawan", "Pampanga", "Pangasinan", "Quezon", "Quezon City",
    "Quirino", "Rizal", "Romblon", "Samar", "Sarangani", "Siquijor",
    "Sorsogon", "South Cotabato", "South Manila", "Southern Mindoro",
    "Southern Leyte", "Sultan Kudarat", "Surigao del Norte",
    "Surigao del Sur", "Tacloban City", "Tarlac", "Upper Kalinga",
    "Zambales", "Zamboanga City", "Zamboanga del Norte",
    "Zamboanga del Sur", "Zamboanga Sibugay",
}

G4_TERMINALS = {
    "name": G4_OFFICE_NAMES,
    "region_keyword": {"Region"},
    "deo_full": {"District Engineering Office"},
    "deo_abbrev": {"DEO"},
    "ordinal": {"1st", "2nd", "3rd", "4th", "5th", "6th", "7th"},
    "roman": {
        "I", "II", "III", "IV-A", "IV-B", "V", "VI", "VII",
        "VIII", "IX", "X", "XI", "XII", "XIII",
    },
    "special_region": {"NCR", "CAR", "NIR"},
    "space": {" "},
}

G4_TRANSITIONS = {
    ("q0", "name"): ["q1"],
    ("q0", "region_keyword"): ["q8"],
    ("q0", "special_region"): ["q11"],
    ("q1", "space"): ["q2"],
    ("q2", "deo_full"): ["q3"],
    ("q2", "deo_abbrev"): ["q4"],
    ("q2", "ordinal"): ["q5"],
    ("q5", "space"): ["q6"],
    ("q6", "deo_full"): ["q7"],
    ("q6", "deo_abbrev"): ["q7"],
    ("q8", "space"): ["q9"],
    ("q9", "roman"): ["q10"],
}
