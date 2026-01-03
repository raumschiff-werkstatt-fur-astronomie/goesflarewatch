# Testing the Translation Workflow

This guide shows you how to test that the translation scripts preserve your existing translations and work correctly with Poedit.

## Quick Test (Automated)

Run the test script:

```bash
./test_translation_workflow.sh
```

This will:
- Check that existing translations are preserved
- Run the translation script
- Verify translations weren't lost
- Show statistics about fuzzy and untranslated entries

## Manual Testing Steps

### Test 1: Verify Existing Translations Are Preserved

1. **Check current state:**
   ```bash
   # Count existing translations
   grep -c "^msgstr \"" locales/de/LC_MESSAGES/index.po
   ```

2. **Make a note of a specific translation:**
   ```bash
   # Find a specific entry (e.g., "Welcome")
   grep -A 1 "Welcome to the Solar Flare Alert" locales/de/LC_MESSAGES/index.po
   ```
   Note the translation value.

3. **Run the translation script:**
   ```bash
   python translate_po.py de
   ```

4. **Verify the translation is still there:**
   ```bash
   # Check the same entry again
   grep -A 1 "Welcome to the Solar Flare Alert" locales/de/LC_MESSAGES/index.po
   ```
   ✅ The translation should be **exactly the same** as before.

### Test 2: Verify Fuzzy Entries Are Preserved

1. **Create a test scenario with fuzzy entries:**
   ```bash
   # First, modify an RST file to create a fuzzy entry
   # Edit index.rst and change a string that's already translated
   # For example, change "Welcome to the Solar Flare Alert Documentation!"
   # to "Welcome to the Solar Flare Alert Documentation! (Updated)"
   ```

2. **Update translations (this will create fuzzy entries):**
   ```bash
   python update_translations.py de
   # Answer 'n' when asked about auto-translation
   ```

3. **Check for fuzzy entries:**
   ```bash
   # Count fuzzy entries
   grep -c "^#, fuzzy" locales/de/LC_MESSAGES/index.po
   ```

4. **Run translate_po.py:**
   ```bash
   python translate_po.py de
   ```

5. **Verify fuzzy entries are still there:**
   ```bash
   # Count fuzzy entries again
   grep -c "^#, fuzzy" locales/de/LC_MESSAGES/index.po
   ```
   ✅ The count should be **the same** (fuzzy entries preserved).

6. **Open in Poedit to see fuzzy entries:**
   ```bash
   poedit locales/de/LC_MESSAGES/index.po
   ```
   ✅ Fuzzy entries should appear with a **yellow background**.

### Test 3: Verify New Strings Are Translated

1. **Add a new string to an RST file:**
   ```bash
   # Edit index.rst and add a new paragraph with text that doesn't exist yet
   # For example, add: "This is a new test paragraph."
   ```

2. **Update translations:**
   ```bash
   python update_translations.py de
   # Answer 'y' when asked about auto-translation
   ```

3. **Check the new translation:**
   ```bash
   # Search for the new string
   grep -A 1 "This is a new test paragraph" locales/de/LC_MESSAGES/index.po
   ```
   ✅ The `msgstr` should be **translated** (not empty).

### Test 4: Test with Poedit

1. **Open a PO file in Poedit:**
   ```bash
   poedit locales/de/LC_MESSAGES/index.po
   ```

2. **Make a manual edit:**
   - Find any translated entry
   - Change the translation to something custom (e.g., "Meine eigene Übersetzung")
   - Save the file

3. **Run translate_po.py again:**
   ```bash
   python translate_po.py de
   ```

4. **Verify your manual edit is preserved:**
   ```bash
   # Check the entry you edited
   grep -A 1 "Meine eigene Übersetzung" locales/de/LC_MESSAGES/index.po
   ```
   ✅ Your custom translation should still be there.

5. **Open in Poedit again:**
   ```bash
   poedit locales/de/LC_MESSAGES/index.po
   ```
   ✅ Your manual edit should still be visible.

### Test 5: Test Fuzzy Translation Flag

1. **Create fuzzy entries** (see Test 2, steps 1-2)

2. **Run with --translate-fuzzy flag:**
   ```bash
   python translate_po.py de --translate-fuzzy
   ```

3. **Check that fuzzy entries were translated:**
   ```bash
   # Count fuzzy entries (should be 0 or reduced)
   grep -c "^#, fuzzy" locales/de/LC_MESSAGES/index.po
   ```
   ✅ Fuzzy entries should be translated and fuzzy flag removed.

## Expected Results Summary

| Test | Expected Result |
|------|----------------|
| Existing translations preserved | ✅ Same translations after running script |
| Fuzzy entries preserved | ✅ Fuzzy entries remain (unless `--translate-fuzzy` used) |
| New strings translated | ✅ New untranslated strings get translated |
| Manual edits preserved | ✅ Your Poedit edits are never overwritten |
| Statistics shown | ✅ Script shows counts of translated/preserved/fuzzy |

## Troubleshooting

### If translations are being overwritten:
- Make sure you're not using `--translate-fuzzy` flag
- Check that the script version is the latest (should preserve existing translations)

### If fuzzy entries are being translated:
- This only happens with `--translate-fuzzy` flag
- Without the flag, fuzzy entries should be preserved

### If new strings aren't being translated:
- Check that the string is actually new (not in the PO file)
- Verify the translation service is working (check internet connection)
- Look for error messages in the script output

## Quick Verification Commands

```bash
# Count total translations
grep -c "^msgstr \"" locales/de/LC_MESSAGES/index.po

# Count fuzzy entries
grep -c "^#, fuzzy" locales/de/LC_MESSAGES/index.po

# Count untranslated entries
grep -c "^msgstr \"\"$" locales/de/LC_MESSAGES/index.po

# Show a sample entry
grep -A 2 "Welcome" locales/de/LC_MESSAGES/index.po
```

