def get_fields_linked_backwards(settings):
    result = {}
    for record_type in settings:
        res = _get_fields_linked_backwards_for_one_type(settings[record_type])
        if len(res):
            result[record_type] = res
    return result


def _get_fields_linked_backwards_for_one_type(obj, result=None):
    if result is None:
        result = []
    if isinstance(obj, dict):
        # If this dict has both 'field' and 'is_backwards_linked', collect them
        if (
            "field" in obj
            and "is_backwards_linked" in obj
            and obj["is_backwards_linked"] == True
        ):
            result.append(obj["field"])
        # Otherwise, recurse on all the values
        for value in obj.values():
            _get_fields_linked_backwards_for_one_type(value, result)
    elif isinstance(obj, list):
        # If list, process each item
        for item in obj:
            _get_fields_linked_backwards_for_one_type(item, result)
    return result
