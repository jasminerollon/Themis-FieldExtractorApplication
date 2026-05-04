def run_fsa(token_string: str) -> dict:
    tokens = [t.strip() for t in token_string.strip().split() if t.strip()]

    if not tokens:
        return {"matched": False, "value": ""}

    SPECIAL = {"NCR", "CAR", "NIR", "BARMM"}

    ROMAN = {
        "I", "II", "III", "IV-A", "IV-B", "V", "VI", "VII",
        "VIII", "IX", "X", "XI", "XII", "XIII"
    }

    if len(tokens) == 1 and tokens[0] in SPECIAL:
        return {"matched": True, "value": token_string}

    if len(tokens) == 2 and tokens[0] == "Region" and tokens[1] in ROMAN:
        return {"matched": True, "value": token_string}

    if len(tokens) >= 4 and tokens[-3:] == ["District", "Engineering", "Office"]:

        name_tokens = tokens[:-3]
        name = " ".join(name_tokens)

        VALID_NAMES = {
            "Abra", "Agusan del Norte", "Agusan del Sur", "Aklan", "Albay",
            "Antique", "Apayao", "Aurora", "Bacolod City", "Baguio",
            "Bataan", "Batanes", "Batangas", "Benguet", "Biliran",
            "Bohol", "Bukidnon", "Bulacan", "Butuan City", "Cagayan",
            "Cagayan de Oro City", "Camarines Norte", "Camarines Sur",
            "Camiguin", "Capiz", "Catanduanes", "Cavite", "Cebu",
            "Cebu City", "Cotabato", "Davao City", "Davao del Norte",
            "Davao del Sur", "Davao de Oro", "Davao Occidental",
            "Davao Oriental", "Dinagat Islands", "Eastern Samar",
            "Guimaras", "Ifugao", "Isabela", "Iligan City",
            "Ilocos Norte", "Ilocos Sur", "Iloilo", "Iloilo City",
            "Laguna", "Lanao del Norte", "La Union", "Leyte",
            "Malabon-Navotas", "Marinduque", "Masbate", "Metro Manila",
            "MIMAROPA", "Mindoro Occidental", "Mindoro Oriental",
            "Misamis Occidental", "Misamis Oriental", "Mountain Province",
            "Negros Occidental", "Negros Oriental", "Nueva Ecija",
            "Nueva Vizcaya", "Palawan", "Pampanga", "Pangasinan",
            "Quezon", "Quezon City", "Quirino", "Rizal", "Romblon",
            "Samar", "Sarangani", "Siquijor", "Sorsogon",
            "South Cotabato", "Southern Leyte", "Sultan Kudarat",
            "Surigao del Norte", "Surigao del Sur", "Tacloban City",
            "Tarlac", "Zambales", "Zamboanga City",
            "Zamboanga del Norte", "Zamboanga del Sur",
            "Zamboanga Sibugay"
        }

        if name in VALID_NAMES:
            return {"matched": True, "value": token_string}

        return {"matched": False, "value": ""}

    if len(tokens) == 2 and tokens[1] == "DEO":

        ordinal = tokens[0]

        if ordinal.endswith(("st", "nd", "rd", "th")):
            return {"matched": True, "value": token_string}

        return {"matched": False, "value": ""}

    return {"matched": False, "value": ""}