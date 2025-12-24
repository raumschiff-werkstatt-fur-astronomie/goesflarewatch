#!/usr/bin/env python3
"""
Update translations after modifying .rst files.

This script:
1. Regenerates .pot template files from .rst sources
2. Updates existing .po files with new/changed strings
3. Optionally auto-translates new strings

Run: python update_translations.py
"""

import os
import subprocess
import sys

def regenerate_pot_files():
    """Regenerate .pot template files from .rst sources."""
    print("Step 1: Regenerating .pot template files...")
    os.chdir("docs")
    try:
        result = subprocess.run(
            ["python", "-m", "sphinx", "-b", "gettext", ".", "_build/gettext"],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            print(f"Error generating .pot files: {result.stderr}")
            return False
        
        # Copy .pot files to templates directory
        print("  Copying .pot files to templates directory...")
        subprocess.run(["mkdir", "-p", "locales/templates"])
        subprocess.run(["cp", "-r", "_build/gettext/*.pot", "locales/templates/"], shell=True)
        subprocess.run(["cp", "-r", "_build/gettext/source", "locales/templates/"], shell=True)
        
        print("✓ Template files regenerated\n")
        return True
    finally:
        os.chdir("..")

def update_po_files():
    """Update .po files using sphinx-intl or msgmerge."""
    print("Step 2: Updating .po files with new strings...")
    
    # Check if sphinx-intl is available
    try:
        import sphinx_intl
        use_sphinx_intl = True
    except ImportError:
        use_sphinx_intl = False
        print("  Note: sphinx-intl not found, using msgmerge instead")
    
    os.chdir("docs")
    try:
        if use_sphinx_intl:
            # Use sphinx-intl to update
            result = subprocess.run(
                ["sphinx-intl", "update", "-p", "_build/gettext", "-l", "de"],
                capture_output=True,
                text=True
            )
        else:
            # Use msgmerge manually for each .po file
            print("  Updating .po files with msgmerge...")
            import glob
            po_files = glob.glob("locales/de/LC_MESSAGES/**/*.po", recursive=True)
            pot_files = glob.glob("locales/templates/**/*.pot", recursive=True)
            
            for po_file in po_files:
                # Find corresponding .pot file
                rel_path = po_file.replace("locales/de/LC_MESSAGES/", "")
                pot_file = f"locales/templates/{rel_path.replace('.po', '.pot')}"
                
                if os.path.exists(pot_file):
                    subprocess.run([
                        "msgmerge", "--update", "--no-fuzzy-matching",
                        po_file, pot_file
                    ], capture_output=True)
        
        print("✓ .po files updated\n")
        return True
    except Exception as e:
        print(f"Error updating .po files: {e}")
        return False
    finally:
        os.chdir("..")

def translate_new_strings():
    """Auto-translate new strings in .po files."""
    response = input("Step 3: Auto-translate new/changed strings? (y/n): ")
    if response.lower() != 'y':
        print("Skipping auto-translation\n")
        return
    
    print("Auto-translating new strings...")
    # Import and run the translation script
    try:
        from translate_po import main as translate_main
        translate_main()
    except ImportError:
        print("Error: translate_po.py not found or dependencies missing")
        print("Run: pip install polib googletrans==4.0.0rc1")
    except Exception as e:
        print(f"Error during translation: {e}")

def main():
    """Main workflow."""
    print("=" * 60)
    print("Translation Update Workflow")
    print("=" * 60)
    print()
    
    # Step 1: Regenerate templates
    if not regenerate_pot_files():
        print("Failed to regenerate templates. Exiting.")
        return
    
    # Step 2: Update PO files
    if not update_po_files():
        print("Failed to update PO files. Exiting.")
        return
    
    # Step 3: Optional auto-translation
    translate_new_strings()
    
    print("=" * 60)
    print("✓ All done! Your translations are updated.")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Review the translations (especially 'fuzzy' entries)")
    print("2. Commit the updated .po files")
    print("3. Rebuild your documentation")

if __name__ == "__main__":
    main()

