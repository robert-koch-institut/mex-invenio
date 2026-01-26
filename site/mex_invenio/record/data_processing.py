from flask import current_app
from typing import Any, List, TypedDict
from typing_extensions import NotRequired


class NormalisedValue(TypedDict):
    url: str
    display_data: dict
    email: NotRequired[str]
    core: NotRequired[str]


def create_display_data_obj(value, language):
    return {"value": value, "language": language}


def normalised_value(
    display_value: str = "",
    url: str = "",
    language: str = "en",
    email: str = "",
    core: str = "",
) -> NormalisedValue:
    return {
        "url": url,
        "display_data": create_display_data_obj(
            display_value if display_value else url, language
        ),
        "email": email,
        "core": core,
    }


def group_values(normalised_values: list) -> list[NormalisedValue]:
    grouped = {}
    for v in normalised_values:
        url = v["url"]
        if url not in grouped:
            grouped[url] = {"display_data": [], "email": None, "core": None}
        grouped[url]["display_data"].append(v["display_data"])
        if grouped[url]["email"] is None:
            grouped[url]["email"] = v.get("email")
        if grouped[url]["core"] is None:
            grouped[url]["core"] = v.get("core")

    return [
        {
            "url": url,
            "display_data": data["display_data"],
            "email": data["email"],
            "core": data["core"],
        }
        for url, data in grouped.items()
    ]


def normalise_record_data(record: dict) -> dict:
    data = {}
    data["backwards_linked"] = {}
    custom_fields = record["custom_fields"]
    record_type = record["metadata"]["resource_type"]["id"]
    for field in custom_fields:
        normalised_value = _normalise_value(
            field, record["custom_fields"][field], record_type
        )
        if field == "mex:minTypicalAge":
            print("normalised value: ", normalised_value)
        if normalised_value:
            data.update({field: normalised_value})

    if record["display_data"]:
        for field in record["display_data"]["linked_records"]:
            if field == "backwards_linked":
                for f in record["display_data"]["linked_records"]["backwards_linked"]:
                    normalised_value_dd = _normalise_linked_data(
                        record["display_data"]["linked_records"]["backwards_linked"][f]
                    )
                    if normalised_value_dd:
                        data["backwards_linked"][f] = normalised_value_dd
            else:
                normalised_value_dd = _normalise_linked_data(
                    record["display_data"]["linked_records"][field]
                )
                if normalised_value_dd:
                    data[field] = normalised_value_dd

    print(data)

    return data


def _normalise_value(field_name: str, field_raw_value: Any, resource_type: str) -> list:
    if field_name == "mex:minTypicalAge":
        print("raw value: ", field_raw_value)
    if not field_raw_value or current_app.config.get("FIELD_TYPES") is None:
        return []

    # Normalise into list
    if not isinstance(field_raw_value, list):
        values = [field_raw_value]
    else:
        values = field_raw_value

    print(f"{values=}")

    # Determine field type
    field_types = current_app.config.get("FIELD_TYPES").get(resource_type, {})
    ftype = field_types.get(field_name)

    if field_name == "mex:minTypicalAge":
        print("ftype: ", ftype)

    # --- type handlers ---
    if field_name in current_app.config.get("EXT_IDS", {}):
        return _normalise_extid(values, field_name)

    elif ftype == "identifier":
        return []

    elif ftype == "text":
        return _normalise_text(values)

    elif ftype == "url":
        return _normalise_url(values)

    elif ftype == "date":
        return _normalise_date(values)

    elif ftype == "label":
        return _normalise_label(values)

    else:
        normalised = [normalised_value(display_value=str(v)) for v in values]
        return group_values(normalised)


# -----------------------
# helper normalisers
# -----------------------


def _normalise_linked_data(values: list) -> list[NormalisedValue]:
    normalised = []
    for v in values:
        for dv in v["display_value"]:
            core_record = v.get("core", "")
            if core_record:
                url = "/records/mex/" + v["link_id"]
            else:
                url = v["link_id"]
            nvalue = normalised_value(
                display_value=dv.get("value", ""),
                language=dv.get("language", ""),
                url=url,
                email=v.get("email", ""),
                core=v.get("core", ""),
            )
            normalised.append(nvalue)
    return group_values(normalised)


def _normalise_date(values: list) -> list[NormalisedValue]:
    normalised = []
    months = {
        "01": "Jan",
        "02": "Feb",
        "03": "Mar",
        "04": "Apr",
        "05": "May",
        "06": "Jun",
        "07": "Jul",
        "08": "Aug",
        "09": "Sep",
        "10": "Oct",
        "11": "Nov",
        "12": "Dec",
    }

    for val in values:
        if not isinstance(val, str):
            normalised.append(normalised_value(display_value=str(val)))
            continue

        if len(val) in (10, 20):  # YYYY-MM-DD or timestamp
            year, month, day = val[0:4], val[5:7], val[8:10]
            normalised.append(
                normalised_value(
                    display_value=f"{months.get(month, month)} {int(day)}, {year}"
                )
            )
        elif len(val) == 7:  # YYYY-MM
            year, month = val[0:4], val[5:7]
            normalised.append(
                normalised_value(display_value=f"{months.get(month, month)} {year}")
            )
        else:  # YYYY
            normalised.append(normalised_value(display_value=val))

    return group_values(normalised)


def _normalise_text(values: list) -> list[NormalisedValue]:
    normalised = []
    for v in values:
        if isinstance(v, dict):
            normalised.append(
                normalised_value(
                    display_value=v.get("value", ""), language=v.get("language", "")
                )
            )
        else:
            normalised.append(normalised_value(display_value=str(v)))

    return group_values(normalised)


def _normalise_url(values: list) -> list[NormalisedValue]:
    normalised = []
    for val in values:
        if not isinstance(val, dict):
            normalised.append(normalised_value(url=str(val)))
            continue

        normalised.append(
            normalised_value(
                display_value=val.get("title", ""),
                language=val.get("language", ""),
                url=val.get("url", ""),
            )
        )
    return group_values(normalised)


def _normalise_extid(values: list, field_name: str) -> list[NormalisedValue]:
    normalised = []
    for val in values:
        if not isinstance(val, str):
            normalised.append(normalised_value(display_value=str(val)))
        else:
            displayed = val
            if val.startswith("http"):
                for prefix in (
                    current_app.config.get("EXT_IDS").get(field_name).get("prefixes")
                ):
                    if val.startswith(prefix):
                        displayed = val.replace(prefix, "")
                        break
                normalised.append(normalised_value(url=val, display_value=displayed))
            else:
                normalised.append(normalised_value(display_value=val))
    return group_values(normalised)


def _normalise_label(values: List) -> List[NormalisedValue]:
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
    return group_values(normalised)
