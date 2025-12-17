import argparse

import polib
import os
from pathlib import Path


def create_entry_key(entry):
    """Create unique key for PO entry combining msgctxt and msgid."""
    if entry.msgctxt:
        return f"{entry.msgctxt}|{entry.msgid}"
    else:
        return entry.msgid


def merge_translations(instance_path: str, language: str, merge_ui: bool = True) -> None:
    """Merge mex-model language with ui.po, giving precedence to ui.po entries."""
    
    # Load mex-model (base translations)
    # Find mex package location relative to this script
    try:
        import mex.model
        mex_model_path = Path(mex.model.__file__).parent
        de_po_path = mex_model_path / "i18n" / f"{language}.po"
        
        if not de_po_path.exists():
            print(f"Mex model {language}.po file not found: {de_po_path}")
            return
        
        base_po = polib.pofile(str(de_po_path))
    except ImportError:
        print("Could not import mex.model package")
        return
    print(f"Processing language: {language}\nLoaded {len(base_po)} entries from mex-model {language}.po (base)")
    
    if merge_ui:
        # Load ui.po (override translations)
        ui_po_path = os.path.join(instance_path, f"translations/{language}/LC_MESSAGES/ui.po")
        
        if not os.path.exists(ui_po_path):
            print(f"UI translations file not found: {ui_po_path}")
            print("Will create messages.po with only mex-model translations")
            ui_po = polib.POFile()
        else:
            ui_po = polib.pofile(ui_po_path)
            print(f"Loaded {len(ui_po)} entries from ui.po (override)")
    else:
        print("Skipping ui.po merge (merge_ui=False)")
        ui_po = polib.POFile()
    
    # Create output messages.po
    messages_po = polib.POFile()
    
    # Copy metadata from base file
    if base_po.metadata:
        messages_po.metadata = base_po.metadata.copy()
        # Update some metadata for the merged file
        messages_po.metadata['POT-Creation-Date'] = ''  # Will be updated
        messages_po.metadata['PO-Revision-Date'] = ''   # Will be updated
    
    # Build lookup from ui.po for exact matching (msgid + msgctxt)
    ui_lookup = {}
    if merge_ui:
        for entry in ui_po:
            if entry.msgid:  # Include entries with empty msgstr too
                key = create_entry_key(entry)
                ui_lookup[key] = entry
        
        print(f"Built override lookup with {len(ui_lookup)} entries from ui.po")
    
    # Track statistics
    base_used = 0
    ui_overrides = 0
    ui_only = 0
    
    # Start with all base entries
    base_keys_processed = set()
    
    for base_entry in base_po:
        if not base_entry.msgid:
            continue
            
        key = create_entry_key(base_entry)
        base_keys_processed.add(key)
        
        # Check if ui.po has an exact match (msgid + msgctxt)
        if merge_ui and key in ui_lookup:
            ui_entry = ui_lookup[key]
            
            # Use ui.po entry (precedence)
            new_entry = polib.POEntry(
                msgid=ui_entry.msgid,
                msgstr=ui_entry.msgstr,
                msgctxt=ui_entry.msgctxt.lower() if ui_entry.msgctxt else None,
                comment=ui_entry.comment or base_entry.comment,
                tcomment=ui_entry.tcomment or base_entry.tcomment,
                occurrences=ui_entry.occurrences + base_entry.occurrences,  # Combine occurrences
                flags=list(set(ui_entry.flags + base_entry.flags))  # Combine flags
            )
            
            messages_po.append(new_entry)
            ui_overrides += 1
            
        else:
            # Use base entry
            new_entry = polib.POEntry(
                msgid=base_entry.msgid,
                msgstr=base_entry.msgstr,
                msgctxt=base_entry.msgctxt.lower() if base_entry.msgctxt else None,
                msgid_plural=getattr(base_entry, 'msgid_plural', None),
                msgstr_plural=getattr(base_entry, 'msgstr_plural', {}),
                comment=base_entry.comment,
                tcomment=base_entry.tcomment,
                occurrences=base_entry.occurrences,
                flags=base_entry.flags
            )
            
            messages_po.append(new_entry)
            base_used += 1
    
    # Add ui.po entries that don't exist in base (ui-only entries)
    if merge_ui:
        for ui_entry in ui_po:
            if not ui_entry.msgid:
                continue
                
            key = create_entry_key(ui_entry)
            
            if key not in base_keys_processed:
                # This is a ui-only entry
                new_entry = polib.POEntry(
                    msgid=ui_entry.msgid,
                    msgstr=ui_entry.msgstr,
                    msgctxt=ui_entry.msgctxt.lower() if ui_entry.msgctxt else None,
                    comment=ui_entry.comment,
                    tcomment=ui_entry.tcomment,
                    occurrences=ui_entry.occurrences,
                    flags=ui_entry.flags
                )
                
                messages_po.append(new_entry)
                ui_only += 1
    
    # Print merge statistics
    if merge_ui:
        print(f"\n=== MERGE RESULTS ===")
        print(f"Base entries used (no override): {base_used}")
        print(f"UI entries overriding base: {ui_overrides}")
        print(f"UI-only entries (not in base): {ui_only}")
    else:
        print(f"\n=== COPY RESULTS ===")
        print(f"Base entries copied: {base_used}")
    
    print(f"Total entries in messages.po: {len(messages_po)}")
    
    # Save merged file
    messages_po_path = os.path.join(instance_path, f"translations/{language}/LC_MESSAGES/messages.po")
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(messages_po_path), exist_ok=True)
    
    # Create backup if file exists
    if os.path.exists(messages_po_path):
        backup_path = messages_po_path + ".backup"
        try:
            import shutil
            shutil.copy2(messages_po_path, backup_path)
            print(f"Created backup: {backup_path}")
        except Exception as e:
            print(f"Warning: Could not create backup: {e}")
    
    # Save the merged file
    messages_po.save(messages_po_path)
    action = "merged" if merge_ui else "copied"
    print(f"Saved {action} translations to: {messages_po_path}")
    
    # Show some examples of what was processed
    if merge_ui and ui_overrides > 0:
        print(f"\n=== EXAMPLES OF UI OVERRIDES ===")
        override_count = 0
        for entry in messages_po:
            if entry.msgid:
                key = create_entry_key(entry)
                if key in ui_lookup and override_count < 5:  # Show first 5 examples
                    context_info = f" [{entry.msgctxt}]" if entry.msgctxt else ""
                    print(f"🔄 \"{entry.msgid}\"{context_info} -> \"{entry.msgstr}\"")
                    override_count += 1
        
        if ui_overrides > 5:
            print(f"... and {ui_overrides - 5} more overrides")
    
    if merge_ui and ui_only > 0:
        print(f"\n=== EXAMPLES OF UI-ONLY ENTRIES ===")
        only_count = 0
        for entry in messages_po:
            if entry.msgid:
                key = create_entry_key(entry)
                if key not in base_keys_processed and only_count < 5:  # Show first 5 examples
                    context_info = f" [{entry.msgctxt}]" if entry.msgctxt else ""
                    print(f"➕ \"{entry.msgid}\"{context_info} -> \"{entry.msgstr}\"")
                    only_count += 1
        
        if ui_only > 5:
            print(f"... and {ui_only - 5} more ui-only entries")
    
    if base_used > 0:
        print(f"\n=== EXAMPLES OF BASE ENTRIES ===")
        example_count = 0
        for entry in messages_po:
            if entry.msgid and example_count < 5:  # Show first 5 examples
                if not merge_ui or create_entry_key(entry) not in ui_lookup:
                    context_info = f" [{entry.msgctxt}]" if entry.msgctxt else ""
                    print(f"📋 \"{entry.msgid}\"{context_info} -> \"{entry.msgstr}\"")
                    example_count += 1
                    if example_count >= 5:
                        break
        
        remaining = base_used - example_count
        if remaining > 0:
            print(f"... and {remaining} more base entries")


def main():
    parser = argparse.ArgumentParser(
        description="Merge mex-model {language}.po with ui.po to create messages.po, giving precedence to ui.po"
    )
    parser.add_argument("instance_path", type=str, help="Invenio instance path")
    parser.add_argument("--no-merge-ui", action="store_true", 
                       help="Skip merging with ui.po, only copy from mex-model")
    args = parser.parse_args()

    for language in ['en', 'de']:
        merge_translations(args.instance_path, language, merge_ui=not args.no_merge_ui)


if __name__ == "__main__":
    main()