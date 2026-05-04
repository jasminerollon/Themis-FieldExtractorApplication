import re
from datetime import datetime

def run_fsa(token_string: str) -> dict:
    token_string = token_string.strip()

    if not token_string:
        return {"matched": False, "value": ""}

    long_pattern = r"^(January|February|March|April|May|June|July|August|September|October|November|December)\s(0?[1-9]|[12]\d|3[01]),\s(2018|2019|2020|2021|2022|2023|2024|2025)$"

    long_match = re.match(long_pattern, token_string)

    if long_match:
        try:
            date_obj = datetime.strptime(token_string, "%B %d, %Y")
            return {
                "matched": True,
                "value": token_string
            }
        except ValueError:
            return {"matched": False, "value": ""}


    slash_pattern = r"^(0[1-9]|1[0-2])/(0[1-9]|[12]\d|3[01])/(2018|2019|2020|2021|2022|2023|2024|2025)$"

    slash_match = re.match(slash_pattern, token_string)

    if slash_match:
        try:
            date_obj = datetime.strptime(token_string, "%m/%d/%Y")
            return {
                "matched": True,
                "value": token_string
            }
        except ValueError:
            return {"matched": False, "value": ""}

    return {"matched": False, "value": ""}