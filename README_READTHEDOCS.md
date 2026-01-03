# Read the Docs Setup for Multiple Languages

## Current Setup

Your documentation supports multiple languages:
- **English (en)**: Main project - `solar-flare-alert`
- **German (de)**: Translation project - `solar-flare-alert-de`
- **Swiss Standard German (de-CH)**: Translation project - `solar-flare-alert-de-ch` (to be created)

## Setting Up Swiss Standard German (de-CH) on Read the Docs

### Step 1: Create the de-CH Project

1. Go to https://readthedocs.org/dashboard/
2. Click **"Import a Project"** or **"Create Project"**
3. Import the same repository: `raumschiff-werkstatt-fur-astronomie/goesflarewatch`
4. Fill in:
   - **Project Name**: `solar-flare-alert-de-ch`
   - **Repository URL**: `https://github.com/raumschiff-werkstatt-fur-astronomie/goesflarewatch.git`
   - **Default branch**: `master`
   - **Language**: **Swiss German (gsw)** or **German (de)** (Read the Docs may not have de-CH, so use de and we'll configure it)
   - **Project slug**: `solar-flare-alert-de-ch`

### Step 2: Configure Language in Advanced Settings

1. Go to the new project's **"Admin"** → **"Advanced Settings"**
2. Look for language settings or environment variables
3. You may need to set a custom environment variable or use the language setting

**Note:** Read the Docs might not recognize `de-CH` directly. You have two options:

**Option A:** Use `de` as the language in Read the Docs, but point to `de-CH` locale files
- This works if Read the Docs uses the `locale_dirs` from your `conf.py`
- The `conf.py` already has `locale_dirs = ['locales/']`, so it should find `de-CH` automatically when you build with `language=de-CH`

**Option B:** Use a custom build command
- In Advanced Settings, you might be able to override the language with an environment variable

### Step 3: Link as Translation

1. Go back to your main project: `solar-flare-alert`
2. Go to **"Admin"** → **"Translations"**
3. Add `solar-flare-alert-de-ch` as a translation

### Step 4: Build Configuration

The `.readthedocs.yaml` file will work for all languages. Read the Docs will:
- Build English version with `language=en` (default)
- Build German version with `language=de` 
- Build Swiss German version with `language=de-CH` (if configured)

## URLs After Setup

- English: `https://solar-flare-alert.readthedocs.io/en/latest/`
- German: `https://solar-flare-alert.readthedocs.io/de/latest/`
- Swiss German: `https://solar-flare-alert.readthedocs.io/de-ch/latest/` (or similar)

## Important Note

Read the Docs uses the `language` setting from Sphinx's `conf.py` or build command. Since your `conf.py` has `locale_dirs = ['locales/']`, it will automatically find the correct locale files based on the language code used during the build.

If Read the Docs doesn't support `de-CH` directly, you can:
1. Set the project language to `de` in Read the Docs
2. Use a custom build command that sets `language=de-CH`
3. Or modify the build to use `de-CH` locale files





