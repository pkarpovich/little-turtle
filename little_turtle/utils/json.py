import json


def pretty_print_json(data: dict[str, any]) -> str:
    return json.dumps(data, indent=4, sort_keys=True, ensure_ascii=False)
