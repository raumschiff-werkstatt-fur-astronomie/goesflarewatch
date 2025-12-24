#!/usr/bin/env python3
"""
Simple script to automatically translate PO files.
Uses DeepL API (free tier available) or Google Translate as fallback.

Install dependencies:
    pip install polib deep-translator

For DeepL (recommended): Get free API key from https://www.deepl.com/pro-api
Set it as environment variable: export DEEPL_API_KEY="your-key-here"

Or use Google Translate (no API key needed, but less reliable):
    pip install googletrans==4.0.0rc1

Run from project root: python translate_po.py
"""

import os
import sys

try:
    import polib
except ImportError:
    print("Error: polib not installed. Run: pip install polib")
    sys.exit(1)

# Try different translation services
translator_type = None
translator = None

# Try Google Translate (free, no API key needed)
try:
    from deep_translator import GoogleTranslator
    translator_type = 'google'
    translator = GoogleTranslator(source='en', target='de')
    print("Using Google Translate...")
except ImportError:
    pass

# If Google Translate not available, try DeepL (needs API key)
if not translator_type:
    USE_DEEPL = os.environ.get('DEEPL_API_KEY')
    if USE_DEEPL:
        try:
            from deep_translator import DeepL
            translator_type = 'deepl'
            translator = DeepL(api_key=USE_DEEPL, source='en', target='de')
            print("Using DeepL translator...")
        except ImportError:
            pass

if not translator_type:
    print("Error: No translator available. Install:")
    print("  pip install deep-translator")
    print("\nFor better quality (optional), get free DeepL API key:")
    print("  https://www.deepl.com/pro-api")
    print("  Then set: export DEEPL_API_KEY='your-key'")
    sys.exit(1)

def translate_text(text, target_lang='de', source_lang='en', is_swiss=False):
    """Translate a single text string."""
    if not text or not text.strip():
        return ""
    
    try:
        translated = translator.translate(text)
        # For Swiss German (de-CH), replace ß with ss
        if is_swiss:
            translated = translated.replace('ß', 'ss').replace('ẞ', 'SS')
        return translated
    except Exception as e:
        print(f"    Warning: Translation error: {e}")
        return ""

def translate_po_file(po_file_path, target_lang='de', source_lang='en'):
    """Translate a PO file from English to target language."""
    print(f"\nTranslating {po_file_path}...")
    
    # Load the PO file
    po = polib.pofile(po_file_path)
    
    # Translate each entry
    translated_count = 0
    skipped_count = 0
    
    for entry in po:
        # Skip if already translated
        if entry.msgstr and entry.msgstr.strip():
            skipped_count += 1
            continue
            
        # Skip if no source text
        if not entry.msgid or not entry.msgid.strip():
            continue
        
        # Translate the message
        is_swiss = 'de-CH' in po_file_path
        translated = translate_text(entry.msgid, target_lang, source_lang, is_swiss=is_swiss)
        if translated:
            entry.msgstr = translated
            translated_count += 1
            if translated_count % 10 == 0:
                print(f"  Progress: {translated_count} translated...")
        else:
            print(f"  ⚠ Skipped: {entry.msgid[:50]}...")
    
    # Save the translated PO file
    po.save(po_file_path)
    print(f"✓ Completed! Translated {translated_count} new strings, {skipped_count} already had translations\n")
    return translated_count

def main():
    """Main function to translate all PO files."""
    # Get target language from command line or default to German
    import sys
    target_lang = 'de'  # Default
    target_lang_code = 'de'
    
    if len(sys.argv) > 1:
        lang_arg = sys.argv[1].lower()
        if lang_arg in ['de-ch', 'ch', 'swiss', 'swiss-german']:
            target_lang = 'de'
            target_lang_code = 'de-CH'
        elif lang_arg in ['de', 'german']:
            target_lang = 'de'
            target_lang_code = 'de'
    
    # Find all PO files in the locales directory
    locales_dir = f"docs/locales/{target_lang_code}/LC_MESSAGES"
    
    if not os.path.exists(locales_dir):
        print(f"Error: {locales_dir} not found!")
        return
    
    po_files = []
    for root, dirs, files in os.walk(locales_dir):
        for file in files:
            if file.endswith('.po'):
                po_files.append(os.path.join(root, file))
    
    if not po_files:
        print(f"No PO files found in {locales_dir}")
        return
    
    print(f"Found {len(po_files)} PO files to translate\n")
    
    total_translated = 0
    # Update translator for target language
    global translator
    if target_lang_code == 'de-CH':
        # Swiss Standard German - use German and convert ß to ss
        print(f"\nNote: Translating to Swiss Standard German (de-CH)")
        print("Converting ß to ss for Swiss conventions\n")
        target_lang = 'de'  # Use German as base
    
    translator = GoogleTranslator(source='en', target=target_lang)
    
    for po_file in po_files:
        try:
            count = translate_po_file(po_file, target_lang=target_lang, source_lang='en')
            total_translated += count
        except Exception as e:
            print(f"Error processing {po_file}: {e}\n")
    
    print(f"\n✓ All done! Translated {total_translated} strings across {len(po_files)} files")
    if target_lang_code == 'de-CH':
        print("\n✓ Swiss Standard German: All ß characters have been converted to ss.")

if __name__ == "__main__":
    main()

