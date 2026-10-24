"""Checks for the lamp-site catalog. A documentation change does not add a release."""

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / ".github" / "scripts" / "pack_lamp_site.py"
TOOLS = ROOT / "tools"


def pack(source, dest):
    return subprocess.run(
        [sys.executable, str(PACK), str(source), str(dest)],
        capture_output=True,
        text=True,
    )


class PackLampSiteTest(unittest.TestCase):
    def test_current_catalog_packs_without_the_external_library(self):
        with tempfile.TemporaryDirectory() as dest:
            result = pack(TOOLS, dest)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse((Path(dest) / "wifi_manager.py").exists())
            catalog = json.loads((Path(dest) / "versions.json").read_text(encoding="utf-8"))
            latest = [item for item in catalog if item.get("latest") is True]
            self.assertEqual(len(latest), 1)
            names = [entry["name"] for entry in latest[0]["files"]]
            self.assertIn("solar_flare_alert.py", names)
            self.assertNotIn("wifi_manager.py", names)
            self.assertTrue((Path(dest) / "lamp_setup.py").is_file())
            page = (Path(dest) / "update-software.html").read_text(encoding="utf-8")
            self.assertIn("lamp_setup.py", page)
            script = (Path(dest) / "lamp.js").read_text(encoding="utf-8")
            self.assertNotIn("navigator.serial", script)

    def test_a_second_latest_release_is_rejected(self):
        with tempfile.TemporaryDirectory() as source, tempfile.TemporaryDirectory() as dest:
            shutil.copytree(TOOLS, source, dirs_exist_ok=True)
            catalog_path = Path(source) / "versions.json"
            catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
            catalog.append(dict(catalog[0], version="2099.01", latest=True))
            catalog_path.write_text(json.dumps(catalog), encoding="utf-8")
            result = pack(source, dest)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("exactly one latest", result.stderr + result.stdout)

    def test_wifi_manager_cannot_be_published_as_a_program(self):
        with tempfile.TemporaryDirectory() as source, tempfile.TemporaryDirectory() as dest:
            shutil.copytree(TOOLS, source, dirs_exist_ok=True)
            planted = Path(source) / "versions" / "2025.03" / "wifi_manager.py"
            planted.write_text("# external\n", encoding="utf-8")
            result = pack(source, dest)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("wifi_manager.py", result.stderr + result.stdout)


if __name__ == "__main__":
    unittest.main()
