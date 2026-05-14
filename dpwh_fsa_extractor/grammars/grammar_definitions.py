# G1: CONTRACT ID FSA
# Format: dd(l | ll)(dddd | ddddd)
G1_STATES = {
    'q1','q2','q3','q4','q5','q6','q7','q8','q9','q10','q11','q12','q13','q14','q15'
}


G1_START = 'q1'
G1_ACCEPTING = {'q8', 'q9', 'q14', 'q15'}


G1_TERMINALS = {
    'digit': set('0123456789'),
    'letters': set('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
}


G1_TRANSITIONS = {
    ('q1','digit'): ['q2'],
    ('q2','digit'): ['q3'],
    ('q3','letters'): ['q4'],
    ('q4','digit'): ['q5'],
    ('q4','letters'): ['q10'],
    ('q5','digit'): ['q6'],
    ('q6','digit'): ['q7'],
    ('q7','digit'): ['q8'],
    ('q8','digit'): ['q9'],
    ('q10','digit'): ['q11'],
    ('q11','digit'): ['q12'],
    ('q12','digit'): ['q13'],
    ('q13','digit'): ['q14'],
    ('q14','digit'): ['q15'],
}


# G2: CONTRACT COST FSA
# Format: (n ∪ nn ∪ nnn)(,nnn)*(.nn)
G2_STATES = {
    'q1','q2','q3','q4','q5','q6','q7','q8','q9','q10','q11'
}


G2_START = 'q1'
G2_ACCEPTING = 'q11'


G2_TERMINALS = {
    'digits': set('0123456789'),
    'comma': {','},
    'dot': {'.'}
}


G2_TRANSITIONS = {
    ('q1','digits'): ['q2'],
    ('q2','comma'): ['q3'],
    ('q2','digits'): ['q4'],
    ('q3','digits'): ['q6'],
    ('q4','comma'): ['q3'],
    ('q4','digits'): ['q5'],
    ('q5','comma'): ['q3'],
    ('q6','digits'): ['q7'],
    ('q7','digits'): ['q8'],
    ('q8','comma'): ['q3'],
    ('q8','dot'): ['q9'],
    ('q9','digits'): ['q10'],
    ('q10','digits'): ['q11']
}


# G3: CONTRACT DATES FSA
# Format: msdcsy


G3_STATES = {
    'q1','q2','q3','q4','q5','q6','q7'
}


G3_START = 'q1'
G3_ACCEPTING = 'q7'


G3_TERMINALS = {
    'month': {
        'January','February','March','April','May','June',
        'July','August','September','October','November','December'
    },
    'space': {' '},
    'digit': set('0123456789'),
    'comma': {','},
    'year': {'2018','2019','2020','2021','2022','2023','2024','2025'}
}


G3_PRODUCTIONS = {
    ('q1','month'): ['q2'],
    ('q2','space'): ['q3'],
    ('q3','digit'): ['q4'],
    ('q4','comma'): ['q5'],
    ('q5','space'): ['q6'],
    ('q6','year'): ['q7']
}


# G4: IMPLEMENTING OFFICE FSA
G4_STATES = {
    'q0','q1','q2','q3','q4','q5','q6','q7','q8','q9','q10'
}


G4_START = 'q0'
G4_ACCEPTING = {'q3', 'q4', 'q7', 'q10'}


G4_TERMINALS = {
    'name': {
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
        'Lanao del Norte', 'Las Piñas-Muntinlupa', 'La Union', 'Leyte',
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
    },
    'region_keyword': {'Region'},
    'deo':     {'District Engineering Office'},
    'ordinal': {'1st', '2nd', '3rd', '4th', '5th', '6th', '7th'},
    'roman':   {'I', 'II', 'III', 'IV-A', 'IV-B', 'V', 'VI', 'VII',
                'VIII', 'IX', 'X', 'XI', 'XII', 'XIII'},
    'space': {' '}
}


G4_PRODUCTIONS = {
    ('q0','name'): ['q1'],
    ('q0','region_keyword'): ['q8'],
    ('q1','space'): ['q2'],
    ('q2','region_keyword'): ['q3'],
    ('q2','deo'): ['q4'],
    ('q2','ordinal'): ['q5'],
    ('q5','space'): ['q6'],
    ('q6','deo'): ['q7'],
    ('q8','space'): ['q9'],
    ('q9','roman'): ['q10']
}