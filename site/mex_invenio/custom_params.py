from invenio_records_resources.services.records.params import ParamInterpreter
import json

class GenericQueryParamsInterpreter(ParamInterpreter):
    def apply(self, identity, search, params):
        """Apply generic query parameters to the search."""
        return search.from_dict(params["raw"])

class TypeLimiterParamsInterpreter(ParamInterpreter):
    def apply(self, identity, search, params):
        """Apply type limiter to the search."""
        resource_type = params.get("resource_type")
        if resource_type:
            search = search.filter("term", metadata__resource_type__id=resource_type)
        # Uncomment this to get a view on the query in development
        # print("#####################################")
        # print(json.dumps(search.to_dict()))
        return search

class HighlightParamsInterpreter(ParamInterpreter):
    def apply(self, identity, search, params):
        """Specify the highlighter fields"""
        search = search.highlight("custom_fields.mex:description.value", "custom_fields.mex:abstract.value")

        # Uncomment this to get a view on the query in development
        print("#########highlight###############")
        print(json.dumps(search.to_dict()))
        return search