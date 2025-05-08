import json
import requests
import os
import click
from jinja2 import Environment, FileSystemLoader
from mex_invenio.config import settings

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

records_dir = 'site/mex_invenio/custom_fields/mex-model/mex/model/entities/'
template_dir = 'templates/semantic-ui/invenio_app_rdm/records/macros'

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


# Main function to process the files
def process_json_files():
    result = {}

    if not os.path.isdir(records_dir):
        return

    for file in os.listdir(records_dir):
        with open(f'{records_dir}/{file}') as f:
            data = json.load(f)

        if data:
            properties = data.get("properties", {})
            resource_type = file.replace("-","").replace(".json","")
            # Initialize the result for this file
            result[resource_type] = {}

            for prop_name, prop_value in properties.items():
                field_type = get_field_type(prop_value)
                if field_type:
                    result[resource_type]["mex:" + prop_name] = field_type
                else:
                    result[resource_type]["mex:" + prop_name] = "unknown"

    return result


@click.command("_field_types")
def _field_types():
    processed_data = process_json_files()
    fields_types = f'{template_dir}/fields_types.jinja'

    with open(fields_types, 'w', encoding='utf-8') as template_file:
        template_file.write("{% set field_types = ")
        template_file.write(json.dumps(processed_data, indent=4))
        template_file.write(" %}")

if __name__ == "__main__":
    _field_types()
