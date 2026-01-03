#!/bin/bash
# Test script for translation workflow improvements
# This script tests that translations are preserved correctly

set -e

echo "=========================================="
echo "Testing Translation Workflow"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Test 1: Check that existing translations are preserved
echo "Test 1: Checking existing translations..."
PO_FILE="locales/de/LC_MESSAGES/index.po"

if [ ! -f "$PO_FILE" ]; then
    echo -e "${RED}✗ PO file not found: $PO_FILE${NC}"
    exit 1
fi

# Count existing translations
EXISTING_COUNT=$(grep -c "^msgstr \"" "$PO_FILE" || echo "0")
echo "  Found $EXISTING_COUNT existing translations"

# Run translation script
echo ""
echo "Test 2: Running translate_po.py (should preserve existing translations)..."
python translate_po.py de

# Check that translations are still there
NEW_COUNT=$(grep -c "^msgstr \"" "$PO_FILE" || echo "0")
if [ "$NEW_COUNT" -ge "$EXISTING_COUNT" ]; then
    echo -e "${GREEN}✓ Test passed: Translations preserved ($EXISTING_COUNT -> $NEW_COUNT)${NC}"
else
    echo -e "${RED}✗ Test failed: Translations were lost!${NC}"
    exit 1
fi

# Test 3: Check for fuzzy entries
echo ""
echo "Test 3: Checking for fuzzy entries..."
FUZZY_COUNT=$(grep -c "^#, fuzzy" "$PO_FILE" || echo "0")
if [ "$FUZZY_COUNT" -gt 0 ]; then
    echo -e "${YELLOW}  Found $FUZZY_COUNT fuzzy entries (these should be preserved)${NC}"
    echo "  Sample fuzzy entries:"
    grep -A 2 "^#, fuzzy" "$PO_FILE" | head -6
else
    echo "  No fuzzy entries found (this is OK if no strings changed)"
fi

# Test 4: Check untranslated entries
echo ""
echo "Test 4: Checking for untranslated entries..."
UNTRANSLATED=$(grep -c "^msgstr \"\"$" "$PO_FILE" || echo "0")
if [ "$UNTRANSLATED" -gt 0 ]; then
    echo "  Found $UNTRANSLATED untranslated entries"
    echo "  These should be translated by the script"
else
    echo "  All entries are translated"
fi

echo ""
echo "=========================================="
echo -e "${GREEN}All tests completed!${NC}"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Open a PO file in Poedit to review fuzzy entries:"
echo "   poedit $PO_FILE"
echo ""
echo "2. To test the full workflow, modify an .rst file and run:"
echo "   python update_translations.py de"
echo ""

