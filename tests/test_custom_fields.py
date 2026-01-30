from invenio_access.permissions import system_identity
from invenio_rdm_records.proxies import current_rdm_records

from tests.data import org_unit_data, resource_data


def test_custom_fields_configured(app_config):
    """Test that the custom fields are configured in the RDM records service."""
    assert len(app_config["RDM_NAMESPACES"].keys()) == 1
    assert len(app_config["RDM_CUSTOM_FIELDS"]) > 0
    # mex:provenance and mex:hasPurpose are not shown in the UI
    assert (
        len(app_config["RDM_CUSTOM_FIELDS_UI"][0]["fields"])
        == len(app_config["RDM_CUSTOM_FIELDS"]) - 2
    )

    # Check that the mex namespace is configured
    assert "mex" in app_config["RDM_NAMESPACES"]

    for cf in app_config["RDM_CUSTOM_FIELDS_UI"][0]["fields"]:
        # Check that all UI config fields have field and props keys
        assert "field" in cf
        assert cf["field"].startswith("mex:")
        assert "props" in cf
        assert isinstance(cf["props"], dict)
        assert "type" in cf["props"]
        # assert 'description' in cf['props']

    # Check that all mex custom fields are in the UI config or are the two exceptions
    for cf in app_config["RDM_CUSTOM_FIELDS"]:
        if cf.name.startswith("mex:"):
            assert cf.name in [
                field["field"]
                for field in app_config["RDM_CUSTOM_FIELDS_UI"][0]["fields"]
            ] + ["mex:provenance", "mex:hasPurpose"]


def test_import_org_unit(
    db, location, resource_type_v, contributors_role_v, import_file
):
    """Test that the CLI command imports the org unit data correctly."""
    service = current_rdm_records.records_service

    messages = import_file("org-unit", org_unit_data)

    search_obj = service.search(system_identity)
    record = list(search_obj.hits)[0]

    rec_cf = record["custom_fields"]

    assert record["metadata"]["title"] == org_unit_data["name"][0]["value"]
    assert rec_cf != {}
    assert rec_cf["mex:identifier"] == org_unit_data["identifier"]
    assert rec_cf["mex:shortName"][0]["value"] == org_unit_data["shortName"][0]["value"]
    assert org_unit_data["unitOf"] == rec_cf["mex:unitOf"]

    # test for the custom field link
    assert len(rec_cf["mex:website"]) == 1
    assert rec_cf["mex:website"][0]["url"] == org_unit_data["website"][0]["url"]

    # test for the custom field multi-language text
    assert len(rec_cf["mex:alternativeName"]) == 1
    assert (
        rec_cf["mex:alternativeName"][0]["value"]
        == org_unit_data["alternativeName"][0]["value"]
    )


class TestLinkCF:
    """Tests for the LinkCF custom field type."""

    def test_link_cf_valid(
        self, db, location, resource_type_v, contributors_role_v, import_file
    ):
        """Test LinkCF accepts valid link data with url, title, and language."""
        data = {
            **org_unit_data,
            "identifier": "test-link-valid-1",
            "website": [
                {"url": "https://example.com", "title": "Example", "language": "en"}
            ],
        }
        import_file("link-valid", data)

        service = current_rdm_records.records_service
        search_obj = service.search(system_identity)
        record = list(search_obj.hits)[0]

        assert record["custom_fields"]["mex:website"][0]["url"] == "https://example.com"
        assert record["custom_fields"]["mex:website"][0]["title"] == "Example"
        assert record["custom_fields"]["mex:website"][0]["language"] == "en"

    def test_link_cf_url_only(
        self, db, location, resource_type_v, contributors_role_v, import_file
    ):
        """Test LinkCF accepts link with only required url field."""
        data = {
            **org_unit_data,
            "identifier": "test-link-url-only-1",
            "website": [{"url": "https://example.com"}],
        }
        import_file("link-url-only", data)

        service = current_rdm_records.records_service
        search_obj = service.search(system_identity)
        record = list(search_obj.hits)[0]

        assert record["custom_fields"]["mex:website"][0]["url"] == "https://example.com"

    def test_link_cf_valid_languages(
        self, db, location, resource_type_v, contributors_role_v, import_file
    ):
        """Test LinkCF accepts valid language codes (en, de)."""
        data = {
            **org_unit_data,
            "identifier": "test-link-lang-1",
            "website": [
                {"url": "https://example.de", "language": "de"},
                {"url": "https://example.com", "language": "en"},
            ],
        }
        import_file("link-lang", data)

        service = current_rdm_records.records_service
        search_obj = service.search(system_identity)
        record = list(search_obj.hits)[0]

        languages = [w["language"] for w in record["custom_fields"]["mex:website"]]
        assert "de" in languages
        assert "en" in languages

    def test_link_cf_multiple_links(
        self, db, location, resource_type_v, contributors_role_v, import_file
    ):
        """Test LinkCF accepts multiple links."""
        data = {
            **org_unit_data,
            "identifier": "test-link-multiple-1",
            "website": [
                {"url": "https://example1.com"},
                {"url": "https://example2.com"},
                {"url": "https://example3.com"},
            ],
        }
        import_file("link-multiple", data)

        service = current_rdm_records.records_service
        search_obj = service.search(system_identity)
        record = list(search_obj.hits)[0]

        assert len(record["custom_fields"]["mex:website"]) == 3


class TestMultiLanguageTextCF:
    """Tests for the MultiLanguageTextCF custom field type."""

    def test_multilang_text_valid(
        self, db, location, resource_type_v, contributors_role_v, import_file
    ):
        """Test MultiLanguageTextCF accepts valid text with language."""
        data = {
            **org_unit_data,
            "identifier": "test-multilang-valid-1",
            "name": [{"value": "Test Organization", "language": "en"}],
        }
        import_file("multilang-valid", data)

        service = current_rdm_records.records_service
        search_obj = service.search(system_identity)
        record = list(search_obj.hits)[0]

        assert record["custom_fields"]["mex:name"][0]["value"] == "Test Organization"
        assert record["custom_fields"]["mex:name"][0]["language"] == "en"

    def test_multilang_text_multiple_languages(
        self, db, location, resource_type_v, contributors_role_v, import_file
    ):
        """Test MultiLanguageTextCF accepts same text in multiple languages."""
        data = {
            **org_unit_data,
            "identifier": "test-multilang-multi-1",
            "name": [
                {"value": "Test Organization", "language": "en"},
                {"value": "Testorganisation", "language": "de"},
            ],
        }
        import_file("multilang-multi", data)

        service = current_rdm_records.records_service
        search_obj = service.search(system_identity)
        record = list(search_obj.hits)[0]

        assert len(record["custom_fields"]["mex:name"]) == 2
        values = [n["value"] for n in record["custom_fields"]["mex:name"]]
        assert "Test Organization" in values
        assert "Testorganisation" in values


class TestFixedEDTFDateStringCF:
    """Tests for the FixedEDTFDateStringCF custom field type."""

    def test_edtf_date_full(
        self, db, location, resource_type_v, contributors_role_v, import_file
    ):
        """Test FixedEDTFDateStringCF accepts full date format YYYY-MM-DD."""
        data = {
            **resource_data,
            "identifier": "test-edtf-full-1",
            "created": "2024-01-15",
        }
        import_file("edtf-full", data)

        service = current_rdm_records.records_service
        search_obj = service.search(system_identity)
        record = list(search_obj.hits)[0]

        assert record["custom_fields"]["mex:created"] == "2024-01-15"

    def test_edtf_date_year_month(
        self, db, location, resource_type_v, contributors_role_v, import_file
    ):
        """Test FixedEDTFDateStringCF accepts year-month format YYYY-MM."""
        data = {
            **resource_data,
            "identifier": "test-edtf-ym-1",
            "created": "2024-03",
        }
        import_file("edtf-ym", data)

        service = current_rdm_records.records_service
        search_obj = service.search(system_identity)
        record = list(search_obj.hits)[0]

        assert record["custom_fields"]["mex:created"] == "2024-03"

    def test_edtf_date_year_only(
        self, db, location, resource_type_v, contributors_role_v, import_file
    ):
        """Test FixedEDTFDateStringCF accepts year-only format YYYY."""
        data = {
            **resource_data,
            "identifier": "test-edtf-year-1",
            "created": "2024",
        }
        import_file("edtf-year", data)

        service = current_rdm_records.records_service
        search_obj = service.search(system_identity)
        record = list(search_obj.hits)[0]

        assert record["custom_fields"]["mex:created"] == "2024"

    def test_edtf_date_multiple(
        self, db, location, resource_type_v, contributors_role_v, import_file
    ):
        """Test FixedEDTFDateStringCF with multiple=True accepts list of dates."""
        data = {
            **resource_data,
            "identifier": "test-edtf-multi-1",
            "start": ["2020-01-01", "2021-06-15"],
        }
        import_file("edtf-multi", data)

        service = current_rdm_records.records_service
        search_obj = service.search(system_identity)
        record = list(search_obj.hits)[0]

        assert len(record["custom_fields"]["mex:start"]) == 2
        assert "2020-01-01" in record["custom_fields"]["mex:start"]
        assert "2021-06-15" in record["custom_fields"]["mex:start"]
