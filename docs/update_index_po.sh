#!/bin/bash
# Simple script to update index.po from index.rst
# Run from docs/ directory

cd "$(dirname "$0")"

echo "Step 1: Generating .pot file from index.rst..."
python -m sphinx -b gettext . _build/gettext

echo ""
echo "Step 2: Updating index.po with new strings..."
if [ -f "_build/gettext/index.pot" ] && [ -f "locales/de/LC_MESSAGES/index.po" ]; then
    msgmerge --update --previous locales/de/LC_MESSAGES/index.po _build/gettext/index.pot
    echo "✓ index.po updated!"
    echo ""
    echo "Changed strings are marked as 'fuzzy' and need review."
    echo "New untranslated strings are empty."
    echo ""
    echo "Next: Run 'python translate_po.py de' to translate new strings"
else
    echo "Error: Files not found"
    exit 1
fi



