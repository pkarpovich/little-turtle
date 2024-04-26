def remove_optional_last_period(text: str) -> str:
    if text[-1] == ".":
        return text[:-1]

    return text
