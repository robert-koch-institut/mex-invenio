from flask import current_app
from typing import Any, List, Dict, Union, Callable

def normalise_record_data(record: dict,  linked_records: dict):
    data = {}
    custom_fields = record["ui"]["custom_fields"]
    record_type = record["ui"]["resource_type"]["id"]
    for field in custom_fields:
        data[field] = _normalise_value(field, record["ui"]["custom_fields"][field], record_type, linked_records)
    return data


def _normalise_value(field_name: str,
                    field_raw_value: Any,
                    resource_type: str,
                    linked_records: dict,
                    backwards_linked: bool = False):
    """
    Normalise values based on type logic from Jinja macros.
    Returns a list of normalised values:
      - plain strings for simple fields
      - dicts {"value": ..., "language": ...} for multilingual text/labels
      - dicts {"url": ..., "display": ...} for extids/urls
      - dicts {"value": ..., "link_id": ...} for identifiers
    """

    if not field_raw_value or current_app.config.get("FIELD_TYPES") is None:
        return []

    # Normalise into list
    if isinstance(field_raw_value, (str, int, float, dict)):
        values = [field_raw_value]
    else:
        values = field_raw_value

    # Determine field type
    field_types = current_app.config.get("FIELD_TYPES").get(resource_type, {})
    ftype = field_types.get(field_name)

    if ftype is None and field_name in current_app.config.get("RECORDS_LINKED_BACKWARDS", {}).get(resource_type, []):
        ftype = current_app.config.get("CUSTOM_TYPES").get("IDENTIFIER")

    # --- type handlers ---
    if field_name in current_app.config.get("EXTIDS", {}):
        return [_normalise_extid(val, field_name) for val in values]

    elif ftype in ("string", "int"):
        return [str(v) for v in values]

    elif ftype == "text":
        return _normalise_text(values, field_name)

    elif ftype == "url":
        return [_normalise_url(val, field_name) for val in values]

    elif ftype == "date":
        return [_normalise_date(val) for val in values]

    elif ftype == "label":
        return _normalise_label(values)

    elif ftype == "identifier":
        return linked_records[field_name]

    else:
        return [str(v) for v in values]


# -----------------------
# helper normalisers
# -----------------------

def _normalise_date(val: str) -> dict[str,str]:
    months = {
        "01": "Jan", "02": "Feb", "03": "Mar", "04": "Apr",
        "05": "May", "06": "Jun", "07": "Jul", "08": "Aug",
        "09": "Sep", "10": "Oct", "11": "Nov", "12": "Dec"
    }
    if not isinstance(val, str):
        return {"display_value": str(val)}

    if len(val) in (10, 20):  # YYYY-MM-DD or timestamp
        year, month, day = val[0:4], val[5:7], val[8:10]
        return {"display_value": f"{months.get(month, month)} {int(day)}, {year}"}
    elif len(val) == 7:  # YYYY-MM
        year, month = val[0:4], val[5:7]
        return {"display_value": f"{months.get(month, month)} {year}"}
    elif len(val) == 4:  # YYYY
        return {"display_value": val}
    return {"display_value": val}


def _normalise_text(values: List[dict], field_name: str) -> List[Dict]:
    """Return as list of {value, language} dicts (preserve all)."""
    normalised = []
    for v in values:
        if isinstance(v, dict):
            normalised.append({"display_value": v.get("value"), "language": v.get("language")})
        else:
            normalised.append({"display_value": str(v), "language": None})
    return normalised


def _normalise_url(val: dict, field_name: str) -> Dict:
    """Preserve URL and multilingual title if available."""
    if not isinstance(val, dict):
        return {"url": str(val), "display_value": None, "language": None}

    return {
        "url": val.get("url"),
        "display_value": val.get("title"),
        "language": val.get("language"),
    }


def _normalise_extid(val: str, field_name: str) -> Dict:
    """Return both raw and display form for external IDs."""
    if not isinstance(val, str):
        return {"url": None, "display_value": str(val)}

    displayed = val
    if val.startswith("http"):
        for prefix in current_app.config.get("EXTIDS").get(field_name).get("urls"):
            if val.startswith(prefix):
                displayed = val.replace(prefix, "")
                break
        return {"url": val, "display_value": displayed}
    return {"url": None, "display_value": val}


def _normalise_label(values: List[str]) -> List[Dict]:
    """Return labels with all available languages."""
    default = {"en": "Invalid label", "de": "Invalid label"}
    results = []
    for v in values:
        if current_app.config.get("PREF_LABELS"):
            label_map = current_app.config.get("PREF_LABELS").get(v, default)
            for lang, text in label_map.items():
                results.append({"display_value": text, "language": lang})
        else:
            results.append({"display_value": v, "language": None})
    return results
