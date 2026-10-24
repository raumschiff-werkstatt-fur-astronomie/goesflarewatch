"""The setup program's replies and the files it is willing to write."""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import lamp_setup  # noqa: E402


class LampSetupTest(unittest.TestCase):
    def test_the_reply_from_this_lamp_is_a_program_without_a_version_file(self):
        text = lamp_setup.parse_exec(b"OKyes\r\nnone\r\n\x04\x04>")
        lines = lamp_setup.parse_lines(text)
        self.assertTrue(lamp_setup.last_flag(lines, "yes", "no"))
        self.assertFalse(lamp_setup.last_flag(lines, "file", "none"))

    def test_a_program_without_version_py_is_the_2025_03_release(self):
        catalog = [{"version": "2025.03", "latest": True}]
        status, version, latest = lamp_setup.judge(True, None, catalog)
        self.assertEqual(status, "current")
        self.assertEqual(version, "2025.03")
        self.assertEqual(latest["version"], "2025.03")

    def test_a_lamp_with_no_program_is_new(self):
        catalog = [{"version": "2025.03", "latest": True}]
        status, version, _latest = lamp_setup.judge(False, None, catalog)
        self.assertEqual((status, version), ("new", None))

    def test_an_older_known_version_is_not_called_current(self):
        catalog = [
            {"version": "2025.03", "latest": False},
            {"version": "2026.01", "latest": True},
        ]
        status, version, latest = lamp_setup.judge(True, "2025.03", catalog)
        self.assertEqual(status, "older")
        self.assertEqual(version, "2025.03")
        self.assertEqual(latest["version"], "2026.01")

    def test_the_device_error_is_not_treated_as_output(self):
        with self.assertRaises(lamp_setup.DeviceError):
            lamp_setup.parse_exec(b"OK\x04Traceback: failed\x04")

    def test_an_unfinished_reply_is_not_accepted(self):
        with self.assertRaises(lamp_setup.ExecError):
            lamp_setup.parse_exec(b"OK yes")

    def test_wifi_manager_and_odd_names_are_refused(self):
        with self.assertRaises(lamp_setup.LampError):
            lamp_setup.safe_device_name("wifi_manager.py")
        with self.assertRaises(lamp_setup.LampError):
            lamp_setup.safe_device_name("../version.py")
        self.assertEqual(lamp_setup.safe_device_name("version.py"), "version.py")

    def test_the_password_record_stays_on_one_line(self):
        self.assertEqual(lamp_setup.wifi_record("Home", "secret"), "Home;secret\n")
        self.assertEqual(lamp_setup.wifi_record("Home", ""), "Home;\n")
        with self.assertRaises(lamp_setup.LampError):
            lamp_setup.wifi_record("a;b", "secret")
        with self.assertRaises(lamp_setup.LampError):
            lamp_setup.wifi_record("", "secret")

    def test_the_local_catalog_loads_the_current_program(self):
        catalog, files = lamp_setup.load_catalog(ROOT / "tools")
        names = [name for name, _data in files]
        self.assertIn("solar_flare_alert.py", names)
        self.assertNotIn("wifi_manager.py", names)
        self.assertEqual(lamp_setup._latest(catalog)["version"], "2025.03")

    def test_german_copy_uses_no_eszett(self):
        for text in lamp_setup.TEXT["de"].values():
            self.assertNotIn("ß", text)
        page = (ROOT / "tools" / "lamp.js").read_text(encoding="utf-8")
        self.assertNotIn("ß", page)


if __name__ == "__main__":
    unittest.main()
