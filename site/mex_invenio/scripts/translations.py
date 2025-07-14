import argparse
from importlib import resources
import polib
import os


def get_translations(instance_path: str) -> None:
    """Merge translations from mex-model with mex-invenio translations."""

    translations_directory = resources.files("mex").joinpath("model/i18n")

    if not translations_directory.is_dir():
        print("Mex model translations directory not found")
        return

    for lang_file in translations_directory.iterdir():
        if lang_file.is_file() and lang_file.name.endswith('.po'):
            lang = lang_file.name[:2]  # Extract language code from filename

            try:
                model_lang_file = polib.pofile(lang_file.as_posix())
                print(f"Loaded {len(model_lang_file)} entries from mex-model {lang_file.name}")
            except IOError as io:
                print(f"I/O error reading {lang_file.name}: {io}")
                return

            translations_file = os.path.join(instance_path, f"translations/{lang}/LC_MESSAGES/instance.po")

            if not os.path.exists(translations_file):
                print(f"Translation file not found: {translations_file}")
                return

            instance_file = polib.pofile(translations_file)
            print(f"Loaded {len(instance_file)} entries from mex-invenio translations")

            # Create a dictionary of existing entries in mex-invenio for quick lookup
            existing_entries = {entry.msgid: entry for entry in instance_file}

            # Track statistics
            added_count = 0
            skipped_count = 0

            # Merge entries from model language file into mex-invenio translations
            # Only add entries that don't already exist (mex-invenio takes precedence)
            for entry in model_lang_file:
                if entry.msgid and entry.msgid not in existing_entries:
                    # Create a new entry for the mex-invenio file
                    new_entry = polib.POEntry(
                        msgid=entry.msgid,
                        msgstr=entry.msgstr,
                        msgid_plural=getattr(entry, 'msgid_plural', None),
                        msgstr_plural=getattr(entry, 'msgstr_plural', {}),
                        msgctxt=getattr(entry, 'msgctxt', None),
                        comment=getattr(entry, 'comment', ''),
                        tcomment=getattr(entry, 'tcomment', ''),
                        flags=getattr(entry, 'flags', [])
                    )
                    instance_file.append(new_entry)
                    added_count += 1
                else:
                    skipped_count += 1

            print(f"Merge complete: {added_count} entries added, {skipped_count} entries skipped (already exist)")

            # Save the merged file
            #backup_file = translations_file + ".backup"
            #print(f"Creating backup: {backup_file}")
            #instance_file.save(backup_file)

            print(f"Saving merged translations to: {translations_file}")
            instance_file.save(translations_file)

            print(f"Total entries in merged file: {len(instance_file)}")

def main():
    parser = argparse.ArgumentParser(description="Process translations.")
    parser.add_argument("instance_path", type=str, help="Invenio instance path")
    args = parser.parse_args()

    get_translations(args.instance_path)

if __name__ == "__main__":
    main()




