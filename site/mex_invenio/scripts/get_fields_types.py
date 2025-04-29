import json
import requests
import os
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
    "/schema/entities/concept/": CUSTOM_TYPES.LABEL,
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


# Function to fetch a JSON file from the GitHub repository
def fetch_json_from_github(file_name):
    url = f"https://raw.githubusercontent.com/robert-koch-institut/mex-model/main/mex/model/entities/{file_name}"
    response = requests.get(url)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching {file_name}: {response.status_code}")
        return None


# Main function to process the files
def process_json_files(file_names):
    result = {}

    for file_name in file_names:
        # Fetch the JSON file from GitHub
        data = fetch_json_from_github(file_name+".json")

        if data:
            properties = data.get("properties", {})
            resource_type = file_name.replace("-","")
            # Initialize the result for this file
            result[resource_type] = {}

            for prop_name, prop_value in properties.items():
                field_type = get_field_type(prop_value)
                if field_type:
                    result[resource_type]["mex:" + prop_name] = field_type
                else:
                    result[resource_type]["mex:" + prop_name] = "unknown"

    return result


# Process the files and get the result
processed_data = process_json_files(settings.ENTITIES)

template_dir = '../../../templates/semantic-ui/invenio_app_rdm/records/macros'
fields_types = f'{template_dir}/fields_types.jinja'

with open(fields_types, 'w', encoding='utf-8') as template_file:
    template_file.write("{% set field_types = ")
    template_file.write(json.dumps(processed_data, indent=4))
    template_file.write(" %}")