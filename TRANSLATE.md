# Simple Translation Guide

## Quick Start (No API Key Needed)

1. **Install dependencies:**
   ```bash
   pip install polib googletrans==4.0.0rc1
   ```

2. **Run the translation script:**
   ```bash
   python translate_po.py
   ```

3. **That's it!** All your PO files will be automatically translated to German.

## Better Quality Translation (Optional - Free API Key)

For better translation quality, use DeepL (free tier: 500,000 characters/month):

1. **Get a free API key:**
   - Go to https://www.deepl.com/pro-api
   - Sign up for free account
   - Get your API key

2. **Set the API key:**
   ```bash
   export DEEPL_API_KEY="your-api-key-here"
   ```

3. **Install DeepL support:**
   ```bash
   pip install deep-translator
   ```

4. **Run the script:**
   ```bash
   python translate_po.py
   ```

## What It Does

- Finds all `.po` files in `docs/locales/de/LC_MESSAGES/`
- Translates only untranslated strings (keeps existing translations)
- Saves the translated files back
- Shows progress as it works

## What Happens When You Modify .rst Files?

When you change your documentation (`.rst` files), you need to update translations:

### Quick Update Workflow:

1. **After modifying .rst files, run:**
   ```bash
   python update_translations.py
   ```

   This will:
   - Regenerate `.pot` template files from your updated `.rst` files
   - Update all `.po` files with new/changed strings
   - Optionally auto-translate new strings

2. **Review fuzzy translations:**
   - Changed strings are marked as "fuzzy" in the `.po` files
   - Review and update these manually or re-run the translation script

3. **Rebuild documentation:**
   ```bash
   cd docs && python -m sphinx -b html -D language=de . _build/html_de
   ```

### Manual Process (if script doesn't work):

1. **Regenerate templates:**
   ```bash
   cd docs
   python -m sphinx -b gettext . _build/gettext
   cp -r _build/gettext/*.pot locales/templates/
   ```

2. **Update PO files:**
   ```bash
   sphinx-intl update -p _build/gettext -l de
   ```

3. **Translate new strings:**
   ```bash
   cd ..
   python translate_po.py
   ```

## Notes

- The script only translates empty `msgstr` entries
- Existing translations are preserved
- You can run it multiple times safely
- Google Translate is free but may have rate limits
- DeepL is more accurate but requires an API key (free tier available)
- Changed strings are marked as "fuzzy" and should be reviewed

