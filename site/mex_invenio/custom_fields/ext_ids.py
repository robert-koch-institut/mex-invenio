def get_ext_ids(obj):
    result = {}
    if isinstance(obj, dict):
        # If this dict has both 'field' and 'prefixes', collect them
        if 'field' in obj and 'prefixes' in obj:
            result[obj['field']] = {'prefixes': obj['prefixes']}
        # Otherwise, recurse on all the values
        for value in obj.values():
            res = get_ext_ids(value)
            result.update(res)
    elif isinstance(obj, list):
        # If list, process each item
        for item in obj:
            res = get_ext_ids(item)
            result.update(res)
    return result