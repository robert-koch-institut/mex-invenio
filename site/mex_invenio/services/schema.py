import re

from flask import current_app
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

    entry_mappings = {
        "Book": "book",
        "Book chapter": "inbook",
        "Conference Paper": "inproceedings",
        "Doctoral thesis": "phdthesis",
        "Habilitation thesis": "phdthesis",
        "Journal Article": "article",
        "Report": "techreport",
        "Preprint": "unpublished",
        "Seminar paper": "unpublished",
        "Thesis": "mastersthesis",
    }

    @staticmethod
    def _normalize_doi(value) -> str:
        DOI_PATTERN = re.compile(r"(10\.\d{4,9}/[-._;()/:A-Za-z0-9]+)")
        if not value:
            return None

        match = DOI_PATTERN.search(value)
        if match:
            return match.group(1)

        # fallback: keep original value
        return value

    @staticmethod
    def _extract_by_lang(field_values) -> str:
        """Returns array of values in users language if available, otherwise all values."""
        by_lang = {}

        if not field_values:
            return []

        for fv in field_values:
            if not fv:
                continue
            lang = fv.get("language", "und")
            if lang in by_lang:
                by_lang[lang].append(fv.get("value"))
            else:
                by_lang[lang] = [fv.get("value")]
        user_lang = str(get_locale())
        if user_lang in by_lang:
            return by_lang[user_lang]
        return [v for values in by_lang.values() for v in values]

    def get_creator(self, obj):
        creator_values = (
            obj["display_data"].get("linked_records", {}).get("mex:creator", [])
        )
        names = [creator["display_value"][0]["value"] for creator in creator_values]
        return " and ".join(names)

    def get_title(self, obj):
        titles = obj.get("custom_fields", {}).get("mex:title", [])
        values = self._extract_by_lang(titles)
        return values[0] if values else None

    def get_publication_year(self, obj):
        return obj.get("custom_fields", {}).get("mex:publicationYear", None)

    def get_journal(self, obj):
        journals = obj.get("custom_fields", {}).get("mex:journal", None)
        values = self._extract_by_lang(journals)
        return " and ".join(values) if values else None

    def get_volume(self, obj):
        return obj.get("custom_fields", {}).get("mex:volume", None)

    def get_issue(self, obj):
        return obj.get("custom_fields", {}).get("mex:issue", None)

    def get_pages(self, obj):
        return obj.get("custom_fields", {}).get("mex:pages", None)

    def get_doi(self, obj):
        value = obj.get("custom_fields", {}).get("mex:doi", None)
        return self._normalize_doi(value)

    def get_abstract(self, obj):
        abstract = obj.get("custom_fields", {}).get("mex:abstract", [])
        abstract = self._extract_by_lang(abstract)
        return abstract[0] if abstract else None

    def get_keywords(self, obj):
        keywords_fields = obj.get("custom_fields", {}).get("mex:keyword", [])
        keywords = [k.get("value") for k in keywords_fields]
        return ", ".join(keywords) if keywords else None

    def resolve_bibtex_type(self, obj):
        """Heuristic-based BibTeX type resolver."""
        cf = obj.get("custom_fields", {})
        rTf = cf.get("mex:bibliographicResourceType")
        rT_label = rTf[0] if rTf else None
        if rT_label:
            resourceType = (
                current_app.config.get("PREF_LABELS").get(rT_label, {}).get("en", "")
            )
            return self.entry_mappings.get(resourceType, "misc")
        return "misc"

    def build_citation_key(self, obj):
        return obj.get("custom_fields", {}).get("mex:identifier")

    def format_field(self, key, value):
        """Format a single BibTeX field."""
        if value is None:
            return None

        if isinstance(value, str):
            value = value.strip()

        if not value:
            return None

        return f"  {key} = {{{value}}}"

    def to_bibtex(self, obj):
        """Convert record dict → BibTeX string."""
        entry_type = self.resolve_bibtex_type(obj)
        fields = self.dump(obj)

        citation_key = self.build_citation_key(obj)

        lines = [f"@{entry_type}{{{citation_key},"]

        for k, v in fields.items():
            formatted = self.format_field(k, v)
            if formatted:
                lines.append(formatted + ",")

        # remove trailing comma from last field (optional polish)
        if len(lines) > 1:
            lines[-1] = lines[-1].rstrip(",")

        lines.append("}")

        return "\n".join(lines)
