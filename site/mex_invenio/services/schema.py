from flask_babel import get_locale
from invenio_rdm_records.services.schemas import RDMRecordSchema
from marshmallow import Schema, fields
from marshmallow_utils.fields import NestedAttribute, SanitizedUnicode


class DisplayDataSchema(Schema):
    """Schema for display data fields."""

    linked_records = fields.Raw(dump_only=True)


class IndexDataSchema(Schema):
    """Schema for index data fields."""

    belongsToLabel = fields.List(SanitizedUnicode(), dump_only=True)
    contributors = fields.List(SanitizedUnicode(), dump_only=True)
    creators = fields.List(SanitizedUnicode(), dump_only=True)
    externalPartners = fields.List(SanitizedUnicode(), dump_only=True)
    externalAssociates = fields.List(SanitizedUnicode(), dump_only=True)
    deFunderOrCommissioners = fields.List(SanitizedUnicode(), dump_only=True)
    enFunderOrCommissioners = fields.List(SanitizedUnicode(), dump_only=True)
    involvedPersons = fields.List(SanitizedUnicode(), dump_only=True)
    enUsedInResource = fields.List(SanitizedUnicode(), dump_only=True)
    deUsedInResource = fields.List(SanitizedUnicode(), dump_only=True)


class MexRDMRecordSchema(RDMRecordSchema):
    """MEX RDM record schema with custom index_data and display_data field."""

    index_data = NestedAttribute(IndexDataSchema, dump_only=True)
    display_data = NestedAttribute(DisplayDataSchema, dump_only=True)


class MExCustomBibTeXSchema(Schema):
    """Custom BibTeX schema replacement."""

    creator = fields.Method("get_creator")
    title = fields.Method("get_title")
    publication_year = fields.Method("get_publication_year")
    journal = fields.Method("get_journal")
    volume = fields.Method("get_volume")
    issue = fields.Method("get_issue")
    pages = fields.Method("get_pages")
    doi = fields.Method("get_doi")
    abstract = fields.Method("get_abstract")
    keywords = fields.Method("get_keywords")

    def get_creator(self, obj):
        creator_values = (
            obj["display_data"].get("linked_records", {}).get("mex:creator", [])
        )
        names = [creator["display_value"][0]["value"] for creator in creator_values]
        return " and ".join(names)

    def _extract_by_lang(self, obj, field):
        """Returns array of values in users language if available, otherwise all values."""
        by_lang = {}
        if field:
            for f in field:
                lang = f.get("language", "und")
                if lang in by_lang:
                    by_lang[lang].append(f.get("value"))
                else:
                    by_lang[lang] = [f.get("value")]
            user_lang = str(get_locale())
            if user_lang in by_lang:
                return by_lang[user_lang]
            return [v for values in by_lang.values() for v in values]
        return []

    def get_title(self, obj):
        titles = obj.get("custom_fields", {}).get("mex:title", [])
        return self._extract_by_lang(obj, titles)[0]

    def get_publication_year(self, obj):
        return obj.get("custom_fields", {}).get("mex:publicationYear", None)

    def get_journal(self, obj):
        journals = obj.get("custom_fields", {}).get("mex:journal", None)
        return " and ".join(self._extract_by_lang(obj, journals))

    def get_volume(self, obj):
        return obj.get("custom_fields", {}).get("mex:volume", None)

    def get_issue(self, obj):
        return obj.get("custom_fields", {}).get("mex:issue", None)

    def get_pages(self, obj):
        return obj.get("custom_fields", {}).get("mex:pages", None)

    def get_doi(self, obj):
        return obj.get("custom_fields", {}).get("mex:doi", None)

    def get_abstract(self, obj):
        abstract = obj.get("custom_fields", {}).get("mex:abstract", [])
        abstract = self._extract_by_lang(obj, abstract)
        return None if not abstract else abstract[0]

    def get_keywords(self, obj):
        keywords_fields = obj.get("custom_fields", {}).get("mex:keyword", [])
        keywords = [k.get("value") for k in keywords_fields]
        return ", ".join(keywords)
