import re

def run_fsa(token_string: str) -> dict:
    token_string = token_string.strip()

    if not token_string:
        return {"matched": False, "value": ""}

    long_pattern = r"^(January|February|March|April|May|June|July|August|September|October|November|December)\s(0?[1-9]|[12]\d|3[01]),\s(19|20)\d{2}$"

    long_match = re.match(long_pattern, token_string)
    if long_match:
        return {
            "matched": True,
            "value": long_match.group(0)
        }

    slash_pattern = r"^(0[1-9]|1[0-2])/(0[1-9]|[12]\d|3[01])/(19|20)\d{2}$"

    slash_match = re.match(slash_pattern, token_string)
    if slash_match:
        return {
            "matched": True,
            "value": slash_match.group(0)
        }

    return {"matched": False, "value": ""}