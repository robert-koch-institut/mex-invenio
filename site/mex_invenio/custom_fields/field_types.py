from mex.model import ENTITY_JSON_BY_NAME


# Custom types definition
class CUSTOM_TYPES:
    STRING = "string"
    INT = "int"
    TEXT = "text"
    URL = "url"
    DATE = "date"
    LABEL = "label"
    IDENTIFIER = "identifier"


# Mapping for JSON $ref checks
CUSTOM_FIELDS_UI_TYPES_AUTO = {
    "/schema/entities/concept#/": CUSTOM_TYPES.LABEL,
    "/schema/entities/": CUSTOM_TYPES.IDENTIFIER,
    "/schema/fields/text": CUSTOM_TYPES.TEXT,
    "/schema/fields/link": CUSTOM_TYPES.URL,
}


# Function to determine the field type based on the provided properties
def get_field_type(property):
    field_type = None

    # Check if $ref exists in the property
    if "$ref" in property:
        ref = property["$ref"]
        for key, value in CUSTOM_FIELDS_UI_TYPES_AUTO.items():
            if ref.startswith(key):
                field_type = value
                break

    # Check if items.$ref exists for array types
    if not field_type and "items" in property:
        if "$ref" in property["items"]:
            ref = property["items"]["$ref"]
        elif "anyOf" in property["items"]:
            if "$ref" in property["items"]["anyOf"][0]:
                ref = property["items"]["anyOf"][0]["$ref"]
            elif "type" in property["items"]:
                ref = property["items"]["anyOf"]["type"]
        elif "type" in property["items"]:
            field_type = property["items"]["type"]

        for key, value in CUSTOM_FIELDS_UI_TYPES_AUTO.items():
            try:
                if ref.startswith(key):
                    field_type = value
                    break
            except NameError:
                pass

    # If no $ref found, check the "type" key
    if not field_type and "type" in property and property["type"] != "array":
        field_type = property["type"]

    # Handle special date types based on "anyOf"
    if not field_type and "anyOf" in property:
        for sub_property in property["anyOf"]:
            if "$ref" in sub_property:
                ref = sub_property["$ref"]
                # Check for matching $ref to get label or field type
                for key, value in CUSTOM_FIELDS_UI_TYPES_AUTO.items():
                    if ref.startswith(key):
                        field_type = value
                        break

            if "pattern" in sub_property:
                if "T" in sub_property["pattern"]:  # Looking for full date-time
                    field_type = CUSTOM_TYPES.DATE
                    break

                # Handle integer types inside anyOf
            if not field_type and "type" in sub_property:
                field_type = sub_property["type"]
                break

    return field_type


# Main function to process the entities from mex-model package
def get_field_types() -> dict:
    """Get field types from Mex model package entities."""
    field_types = {}

    # Use the pre-loaded entity data from mex-model package
    for entity_name, entity_data in ENTITY_JSON_BY_NAME.items():
        try:
            properties = entity_data.get("properties", {})
            resource_type = entity_data.get("$id", "").split("/")[-1].replace("-", "")

            # Initialize the result for this entity
            field_types[resource_type] = {}

            for prop_name, prop_value in properties.items():
                field_type = get_field_type(prop_value)
                if field_type:
                    field_types[resource_type]["mex:" + prop_name] = field_type
                else:
                    field_types[resource_type]["mex:" + prop_name] = "unknown"
        except Exception as e:
            print(f"Error processing entity {entity_name}: {e}")
            continue

    return field_types
