import json
import requests

from flask import current_app


# Define the base URL for the GitHub repository
BASE_URL = "https://raw.githubusercontent.com/robert-koch-institut/mex-model/main/mex/model/entities/"

# Mapping for JSON $ref checks
IDENTIFIER_REF_PREFIX = "/schema/entities/"
LABEL_IDENTIFIER = "concept#"

def extract_entity_name(ref):
    entity = ref.split("/")[3]
    e = entity.replace('#','').replace('-','')
    return e

def is_identifier(ref):
    return ref.startswith(IDENTIFIER_REF_PREFIX) and ref.split("/")[3] != LABEL_IDENTIFIER

# Function to determine if a property is of type 'identifier'
def get_entity_name(property):
    # Check if $ref exists in the property
    if "$ref" in property:
        ref = property["$ref"]
        if is_identifier(ref):
            return {"mex:"+extract_entity_name(ref): []}

    # Check if items.$ref exists for array types
    if "items" in property:
        if "anyOf" in property["items"]:
            entities = {}
            items = property["items"]["anyOf"]
            for i in items:
                if "$ref" in i and is_identifier(i["$ref"]):
                    entities["mex:"+extract_entity_name(i["$ref"])] = []
            return entities
        else:
            if "$ref" in property["items"]:
                ref = property["items"]["$ref"]
                try:
                    if is_identifier(ref):
                        return {"mex:"+extract_entity_name(ref): []}
                except NameError:
                    pass

    # Check if anyOf contains a $ref starting with the identifier prefix
    if "anyOf" in property:
        entities = {}
        for sub_property in property["anyOf"]:
            if "$ref" in sub_property:
                ref = sub_property["$ref"]
                if is_identifier(ref):
                    entities["mex:"+extract_entity_name(ref)] = []
        return entities

    return False

# Dictionary to store the results
identifier_properties = {}

# Process each file
for name in current_app.config.get('ENTITIES', {}):
    # Fetch the JSON file from GitHub
    file_name = name + ".json"
    url = BASE_URL + file_name
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        properties = data.get("properties", {})
        # List to store identifier properties for this file
        identifiers = {}
        for prop_name, prop_value in properties.items():
            entity_names = get_entity_name(prop_value)
            if entity_names:
                identifiers["mex:"+prop_name]=entity_names
        # Add to the result if any identifier properties are found
        if identifiers:
            identifier_properties[name.replace("-","")] = identifiers
    else:
        print(f"Error fetching {file_name}: {response.status_code}")

# Output the result in JSON format
print(json.dumps(identifier_properties, indent=4))
