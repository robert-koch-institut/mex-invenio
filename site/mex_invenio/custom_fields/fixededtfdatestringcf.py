from edtf.parser.edtf_exceptions import EDTFParseException
from invenio_records_resources.services.custom_fields import EDTFDateStringCF


class FixedEDTFDateStringCF(EDTFDateStringCF):
    """EDTF date custom field.

    There is a bug in the EDTFDateStringCF that does not index properly.
    This is described in an issue in invenio-records-resources:
    https://github.com/inveniosoftware/invenio-records-resources/issues/634

    This subclasses the EDTFDateStringCF to fix the issue by overriding the
    dump and load methods to correctly handle multiple dates.
    """

    def dump(self, data, cf_key="custom_fields"):
        """Dump the custom field.

        Gets both the record and the custom fields key as parameters.
        This supports the case where a field is based on others, both
        custom and non-custom fields.
        """
        dates = data[cf_key].get(self.name)
        if dates:
            try:
                if self._multiple:
                    data[cf_key][self.name] = []

                    for date in dates:
                        data[cf_key][self.name].append(self._calculate_date_range(date))
                else:
                    # dates is just one date
                    data[cf_key][self.name] = self._calculate_date_range(dates)
            except EDTFParseException:
                pass

    def load(self, record, cf_key="custom_fields"):
        """Load the custom field.

        Gets both the record and the custom fields key as parameters.
        This supports the case where a field is based on others, both
        custom and non-custom fields.
        """
        dates = record.get(cf_key, {}).pop(self.name, None)
        if dates:
            if self._multiple:
                record[cf_key][self.name] = [d["date"] for d in dates]
            else:
                record[cf_key][self.name] = dates["date"]
