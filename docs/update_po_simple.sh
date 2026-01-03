#!/bin/bash
# Simple script to update PO files from RST files
# Run this from the docs/ directory

set -e

echo "Step 1: Generating .pot files from .rst files..."
python -m sphinx -b gettext . _build/gettext

echo ""
echo "Step 2: Updating .po files with new/changed strings..."
echo "This preserves existing translations and marks changed strings as 'fuzzy'"

# Update index.po specifically
if [ -f "_build/gettext/index.pot" ] && [ -f "locales/de/LC_MESSAGES/index.po" ]; then
    echo "  Updating index.po..."
    msgmerge --update --previous locales/de/LC_MESSAGES/index.po _build/gettext/index.pot
    echo "  ✓ index.po updated"
else
    echo "  ⚠ Files not found"
fi

# Update all other PO files
for po_file in locales/de/LC_MESSAGES/*.po; do
    if [ -f "$po_file" ]; then
        filename=$(basename "$po_file" .po)
        pot_file="_build/gettext/${filename}.pot"
        
        if [ -f "$pot_file" ]; then
            echo "  Updating ${filename}.po..."
            msgmerge --update --previous "$po_file" "$pot_file"
        fi
    fi
done

echo ""
echo "Step 3: Copying .pot files to templates directory..."
mkdir -p locales/templates
cp -r _build/gettext/*.pot locales/templates/ 2>/dev/null || true
cp -r _build/gettext/source locales/templates/ 2>/dev/null || true

echo ""
echo "✓ Done! PO files updated."
echo ""
echo "Next steps:"
echo "1. Review fuzzy entries (changed strings) in Poedit:"
echo "   poedit locales/de/LC_MESSAGES/index.po"
echo ""
echo "2. Translate new untranslated strings:"
echo "   python translate_po.py de"



