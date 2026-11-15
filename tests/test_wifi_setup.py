"""The phone setup page must refuse networks the lamp cannot join."""

import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "tools" / "versions" / "2026.11" / "wifi_setup.py"


def load():
    spec = importlib.util.spec_from_file_location("wifi_setup", MODULE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class WifiSetupTest(unittest.TestCase):
    def setUp(self):
        self.setup = load()

    def test_scan_labels_open_password_and_enterprise_networks(self):
        results = [
            (b"iitk", b"", 1, -70, 0, 0),
            (b"iitk", b"", 1, -58, 0, 0),
            (b"VFA_B1", b"", 6, -48, 3, 0),
            (b"eduroam", b"", 1, -60, 5, 0),
            (b"iitk-sec", b"", 11, -59, 5, 0),
            (b"Solar Flare Alert", b"", 1, -20, 0, 0),
            (b"", b"", 1, -30, 0, 0),
        ]
        found = self.setup.parse_scan(results)
        self.assertEqual(
            [(item["ssid"], item["kind"]) for item in found],
            [("VFA_B1", "password"), ("iitk", "open"), ("iitk-sec", "account"), ("eduroam", "account")],
        )

    def test_the_page_does_not_offer_an_enterprise_network(self):
        networks = self.setup.parse_scan(
            [
                (b"home", b"", 1, -40, 3, 0),
                (b"eduroam", b"", 1, -50, 5, 0),
                (b"iitk", b"", 1, -55, 0, 0),
            ]
        )
        page = self.setup.portal_page(networks, "en")
        self.assertIn('value="home"', page)
        self.assertIn('value="iitk"', page)
        self.assertNotIn('value="eduroam"', page)
        self.assertIn("asks for a username", page)
        self.assertIn("sign-in page", page)
        self.assertIn("personal hotspot", page)
        self.assertIn("not sent to a server", page)
        self.assertNotIn("no Wi-Fi password", page)

    def test_german_page_uses_sie_and_no_eszett(self):
        page = self.setup.portal_page([], "de")
        self.assertIn("Wählen Sie", page)
        self.assertNotIn("ß", page)

    def test_enterprise_choice_saves_nothing(self):
        networks = [{"ssid": "eduroam", "kind": "account"}]
        self.assertEqual(self.setup.decide_join(networks, "eduroam", "secret"), ("refuse", ""))

    def test_open_network_does_not_keep_the_typed_password(self):
        networks = [{"ssid": "iitk", "kind": "open"}]
        self.assertEqual(self.setup.decide_join(networks, "iitk", "secret"), ("open", ""))

    def test_password_network_requires_a_password(self):
        networks = [{"ssid": "home", "kind": "password"}]
        self.assertEqual(self.setup.decide_join(networks, "home", ""), ("need_password", ""))
        self.assertEqual(self.setup.decide_join(networks, "home", "secret"), ("join", "secret"))

    def test_semicolon_is_rejected_and_profiles_round_trip(self):
        networks = [{"ssid": "home", "kind": "password"}]
        self.assertEqual(self.setup.decide_join(networks, "home", "a;b"), ("bad", ""))
        text = self.setup.profiles_text([("home", "secret")])
        self.assertEqual(text, "home;secret\n")
        self.assertEqual(self.setup.parse_profiles(text), [("home", "secret")])

    def test_dns_answer_points_at_the_lamp(self):
        query = b"\x12\x34\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x07captive\x05apple\x03com\x00\x00\x01\x00\x01"
        answer = self.setup.build_dns_response(query)
        self.assertTrue(answer)
        self.assertEqual(answer[:2], b"\x12\x34")
        self.assertEqual(answer[-4:], bytes([192, 168, 4, 1]))

    def test_program_uses_its_own_setup_page(self):
        program = (ROOT / "tools" / "versions" / "2026.11" / "solar_flare_alert.py").read_text(encoding="utf-8")
        self.assertIn("from wifi_setup import WifiSetup", program)
        self.assertNotIn("WifiManager", program)


if __name__ == "__main__":
    unittest.main()
