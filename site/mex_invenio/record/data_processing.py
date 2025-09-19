from flask import current_app
from typing import Any, List, Dict, Union, Callable, TypedDict
from typing_extensions import NotRequired

class NormalisedValue(TypedDict):
    url: str
    display_value:str
    language: str
    email: NotRequired[str]
    
def normalised_value(
        display_value: str = "",
        url: str = "",
        language: str = "en"
    ) -> NormalisedValue:
        return {
            "url": url,
            "display_value": display_value or url or "",
            "language": language,
        }
    

def normalise_record_data(record: dict,  linked_records: dict):
    print("record: ", record)
    data = {}
    data["backwards_linked"] = {}
    custom_fields = record["ui"]["custom_fields"]
    record_type = record["ui"]["resource_type"]["id"]
    for field in custom_fields:
        data[field] = _normalise_value(field, record["ui"]["custom_fields"][field], record_type, linked_records)


    for field in current_app.config.get("RECORDS_LINKED_BACKWARDS", {}).get(record_type, []):
        if field in linked_records["backwards_linked"]:
            data["backwards_linked"][field] = _normalise_identifier(linked_records["backwards_linked"][field])
    return data


def _normalise_value(field_name: str,
                    field_raw_value: Any,
                    resource_type: str,
                    linked_records: dict):
    """
    Normalise values based on type logic from Jinja macros.
    Returns a list of normalised values:
      - plain strings for simple fields
      - dicts {"display_value": ..., "language": ...} for multilingual text/labels
      - dicts {"url": ..., "display_value": ...} for extids/urls
      - dicts {"display_value": ..., "link_id": ...} for identifiers
    """

    if not field_raw_value or current_app.config.get("FIELD_TYPES") is None:
        return []

    # Normalise into list
    if not isinstance(field_raw_value, list):
        values = [field_raw_value]
    else:
        values = field_raw_value

    # Determine field type
    field_types = current_app.config.get("FIELD_TYPES").get(resource_type, {})
    ftype = field_types.get(field_name)
    # --- type handlers ---
    if field_name in current_app.config.get("EXTIDS", {}):
        return _normalise_extid(values, field_name)

    elif ftype in ("string", "int"):
        return [normalised_value(display_value=str(v)) for v in values]

    elif ftype == "text":
        return _normalise_text(values)

    elif ftype == "url":
        return _normalise_url(values)

    elif ftype == "date":
        return _normalise_date(values)

    elif ftype == "label":
        return _normalise_label(values)

    elif ftype == "identifier":
        return _normalise_identifier(linked_records[field_name], field_name=="mex:contact")

    else:
        return [normalised_value(display_value=str(v)) for v in values]

# -----------------------
# helper normalisers
# -----------------------

def _normalise_identifier(values: list, is_contact: bool = False) -> list[NormalisedValue]:
    results = []
    nvalue = {}
    for val in values:
        for t in val["title"]:
            if isinstance(t,dict):
                nvalue = normalised_value(display_value=t.get("value",""), language=t.get("language",""), url="/"+val["link_id"])
            else:
                nvalue = normalised_value(display_value=t, url="/"+val["link_id"])
            if is_contact:
                    nvalue["email"] = val["email"]
            results.append(nvalue)
    return results


def _normalise_date(values: list) -> list[NormalisedValue]:
    normalised = []
    for val in values:
        months = {
            "01": "Jan", "02": "Feb", "03": "Mar", "04": "Apr",
            "05": "May", "06": "Jun", "07": "Jul", "08": "Aug",
            "09": "Sep", "10": "Oct", "11": "Nov", "12": "Dec"
        }
        if not isinstance(val, str):
            normalised.append(normalised_value(display_value=str(val)))

        if len(val) in (10, 20):  # YYYY-MM-DD or timestamp
            year, month, day = val[0:4], val[5:7], val[8:10]
            normalised.append(normalised_value(display_value=f"{months.get(month, month)} {int(day)}, {year}"))
        elif len(val) == 7:  # YYYY-MM
            year, month = val[0:4], val[5:7]
            normalised.append(normalised_value(display_value=f"{months.get(month, month)} {year}"))
        else:  # YYYY
            normalised.append(normalised_value(display_value=val))
    
    return normalised 


def _normalise_text(values: list) -> list[NormalisedValue]:
    normalised = []
    for v in values:
        if isinstance(v, dict):
            normalised.append(normalised_value(display_value=v.get("value", ""), language=v.get("language", "")))
        else:
            normalised.append(normalised_value(display_value=str(v)))
    
    return normalised


def _normalise_url(values: list) -> list[NormalisedValue]:
    normalised = []
    for val in values:
        if not isinstance(val, dict):
            normalised.append(normalised_value(url=str(val)))

        normalised.append(normalised_value(display_value=val.get("title",""), language=val.get("language", ""), url=val.get("url", "")))
    return normalised

def _normalise_extid(values: list, field_name: str) -> list[NormalisedValue]:
    normalised = []
    for val in values:
        if not isinstance(val, str):
            normalised.append(normalised_value(display_value=str(val)))
        else:
            displayed = val
            if val.startswith("http"):
                for prefix in current_app.config.get("EXTIDS").get(field_name).get("urls"):
                    if val.startswith(prefix):
                        displayed = val.replace(prefix, "")
                        break
                normalised.append(normalised_value(url=val, display_value=displayed))
            else:
                normalised.append(normalised_value(display_value=val))
    return normalised


def _normalise_label(values: List[str]) -> List[Dict]:
    """Return labels with all available languages."""
    default = {"en": "Invalid label", "de": "Invalid label"}
    normalised = []
    for v in values:
        if current_app.config.get("PREF_LABELS"):
            label_map = current_app.config.get("PREF_LABELS").get(v, default)
            for lang, text in label_map.items():
                normalised.append(normalised_value(display_value=text, language=lang))
        else:
            normalised.append(normalised_value(display_value=v))
    return normalised
