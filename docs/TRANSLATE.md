# Translation Workflow Guide

**Note:** All translation scripts are located in the `docs/` directory. Run them from there:
```bash
cd docs
```

## Available Languages

- **German (de)**: `python translate_po.py de` or `python translate_po.py`
- **Swiss Standard German (de-CH)**: `python translate_po.py de-CH` or `python translate_po.py ch`

## Quick Start (No API Key Needed)

1. **Install dependencies:**
   ```bash
   pip install polib deep-translator
   ```

2. **Navigate to docs directory:**
   ```bash
   cd docs
   ```

3. **Run the translation script:**
   ```bash
   # For German
   python translate_po.py de
   
   # For Swiss Standard German (de-CH)
   python translate_po.py de-CH
   ```

3. **That's it!** All your PO files will be automatically translated.

**Note for Swiss Standard German (de-CH):** The script automatically converts all "ß" (beta) characters to "ss" to match Swiss conventions.

## Key Features

✅ **Preserves existing translations** - Your manual edits are never overwritten  
✅ **Preserves fuzzy entries** - Changed strings are kept for manual review in Poedit  
✅ **Only translates new strings** - Safe to run multiple times  
✅ **Poedit-friendly** - Fuzzy entries are clearly marked for review

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

- Finds all `.po` files in `locales/de/LC_MESSAGES/`
- **Only translates completely untranslated strings** (preserves all existing translations)
- **Preserves fuzzy entries** for manual review (unless you use `--translate-fuzzy` flag)
- Saves the translated files back
- Shows progress and statistics as it works

## Working with Poedit

The workflow is designed to work seamlessly with Poedit:

1. **After running the translation script**, open `.po` files in Poedit
2. **Fuzzy entries** (marked with a yellow background) need manual review:
   - These are strings where the source text changed
   - Review and update the translation if needed
   - Remove the fuzzy flag when done
3. **New translations** appear in green - review and edit if needed
4. **Existing translations** are preserved and shown normally

### Translating Fuzzy Entries Automatically

If you want to auto-translate fuzzy entries (overwriting existing translations):

```bash
python translate_po.py de --translate-fuzzy
```

⚠️ **Warning**: This will overwrite existing translations for fuzzy entries. Use with caution!

## What Happens When You Modify .rst Files?

When you change your documentation (`.rst` files), you need to update translations:

### Recommended Workflow:

1. **After modifying .rst files, run (from docs directory):**
   ```bash
   cd docs
   python update_translations.py de
   ```

   This will:
   - Regenerate `.pot` template files from your updated `.rst` files
   - Update all `.po` files with new/changed strings (preserving existing translations)
   - Mark changed strings as "fuzzy" for review
   - Optionally auto-translate new untranslated strings

2. **Review and edit in Poedit:**
   ```bash
   # Open any .po file in Poedit
   poedit locales/de/LC_MESSAGES/index.po
   ```
   - Review fuzzy entries (yellow background) - these need manual review
   - Edit translations as needed
   - Remove fuzzy flags when translations are correct

3. **Or auto-translate new strings (from docs directory):**
   ```bash
   cd docs
   python translate_po.py de
   ```
   This will translate only new untranslated strings, preserving everything else.

4. **Rebuild documentation:**
   ```bash
   python -m sphinx -b html -D language=de . _build/html_de
   ```

### Automated Workflow (Non-Interactive):

```bash
# From docs directory: Update translations and auto-translate new strings without prompts
cd docs
python update_translations.py de --auto
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

## Command Reference

### `translate_po.py`

Translate new strings in PO files:

```bash
# All commands should be run from the docs/ directory
cd docs

# Basic usage (German)
python translate_po.py de

# Swiss Standard German
python translate_po.py de-CH

# Also translate fuzzy entries (overwrites existing fuzzy translations)
python translate_po.py de --translate-fuzzy
```

### `update_translations.py`

Update PO files after modifying RST files:

```bash
# From docs directory
cd docs

# Interactive mode (asks for confirmation)
python update_translations.py de

# Non-interactive mode (auto-translates new strings)
python update_translations.py de --auto

# Or use short form
python update_translations.py de -y
```

## Notes

- ✅ **Existing translations are always preserved** - Your manual edits are safe
- ✅ **Fuzzy entries are preserved** - They're marked for review in Poedit
- ✅ **Only untranslated strings are auto-translated** - Safe to run multiple times
- ✅ **Poedit-friendly workflow** - Open any `.po` file in Poedit to review/edit
- ⚠️ **Google Translate** is free but may have rate limits
- ⭐ **DeepL** is more accurate but requires an API key (free tier: 500k chars/month)
- 📝 **Changed strings** are marked as "fuzzy" and should be reviewed in Poedit

