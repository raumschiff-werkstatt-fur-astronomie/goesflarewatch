# The lamp's own Wi-Fi setup. A phone joins the open network "Solar Flare Alert"
# and chooses a network on the page. The password stays on the lamp.

import time

AP_SSID = "Solar Flare Alert"
AP_IP = "192.168.4.1"
WIFI_FILE = "wifi.dat"

TEXT = {
    "en": {
        "lang_link": "Deutsch",
        "lang_other": "de",
        "title": "Solar Flare Alert",
        "intro": "The lamp is not connected to the Wi-Fi, so the light keeps blinking. Choose the network it should join.",
        "only_lamp": "You are connected to the lamp. This network has no password.",
        "password": "Password",
        "join": "Join this network",
        "scan": "Scan again",
        "none": "The lamp cannot see a Wi-Fi network. Move it closer to the router, then scan again.",
        "account": "The lamp cannot join this network. It asks for a username while connecting.",
        "open": "If this network then opens a sign-in page, the lamp cannot fill it in. Use your phone's hotspot instead.",
        "hotspot": "If your only network is one the lamp cannot join, turn on your phone's personal hotspot. Give it a name and a password, then choose that name here. The lamp will use the phone's mobile data.",
        "stays": "The password stays on the lamp. It is not sent to a server.",
        "choose": "Choose a network, then try again.",
        "unknown": "The lamp can no longer see that network. Scan again.",
        "bad": "The name or the password contains a character the lamp cannot store.",
        "need_password": "This network needs a password.",
        "refuse": "The lamp cannot join {ssid}. It asks for a username while connecting. Nothing was saved.",
        "failed": "The lamp could not join {ssid}. Check the password, then try again.",
        "joined": "The lamp has joined {ssid}. It will restart. The light blinks once more, then it stays on. You can leave the Wi-Fi network Solar Flare Alert and return to your own.",
    },
    "de": {
        "lang_link": "English",
        "lang_other": "en",
        "title": "Sonneneruptionsalarm",
        "intro": "Die Lampe ist nicht mit dem WLAN verbunden, deshalb blinkt das Licht. Wählen Sie das Netzwerk, dem sie beitreten soll.",
        "only_lamp": "Sie sind mit der Lampe verbunden. Dieses Netzwerk hat kein Passwort.",
        "password": "Passwort",
        "join": "Diesem Netzwerk beitreten",
        "scan": "Erneut suchen",
        "none": "Die Lampe sieht kein WLAN. Stellen Sie sie näher an den Router und suchen Sie erneut.",
        "account": "Die Lampe kann diesem Netzwerk nicht beitreten. Es verlangt beim Verbinden einen Benutzernamen.",
        "open": "Wenn danach eine Anmeldeseite erscheint, kann die Lampe sie nicht ausfüllen. Benutzen Sie dann den Hotspot Ihres Telefons.",
        "hotspot": "Wenn Sie nur ein Netzwerk haben, dem die Lampe nicht beitreten kann, schalten Sie den persönlichen Hotspot Ihres Telefons ein. Geben Sie ihm einen Namen und ein Passwort, und wählen Sie diesen Namen hier. Die Lampe benutzt dann die mobilen Daten des Telefons.",
        "stays": "Das Passwort bleibt auf der Lampe. Es wird nicht an einen Server gesendet.",
        "choose": "Wählen Sie ein Netzwerk und versuchen Sie es erneut.",
        "unknown": "Die Lampe sieht dieses Netzwerk nicht mehr. Suchen Sie erneut.",
        "bad": "Der Name oder das Passwort enthält ein Zeichen, das die Lampe nicht speichern kann.",
        "need_password": "Dieses Netzwerk braucht ein Passwort.",
        "refuse": "Die Lampe kann {ssid} nicht beitreten. Es verlangt beim Verbinden einen Benutzernamen. Es wurde nichts gespeichert.",
        "failed": "Die Lampe konnte {ssid} nicht beitreten. Prüfen Sie das Passwort und versuchen Sie es erneut.",
        "joined": "Die Lampe ist {ssid} beigetreten. Sie startet neu. Das Licht blinkt noch einmal, danach leuchtet es dauerhaft. Sie können das WLAN Solar Flare Alert verlassen und zu Ihrem eigenen Netzwerk zurückkehren.",
    },
}


def network_kind(auth):
    """Map an ESP32 scan auth code to a network this page can explain."""
    if auth in (5, 10):
        return "account"
    if auth in (0, 9):
        return "open"
    return "password"


def parse_scan(results, own_ssid=AP_SSID):
    """Keep the strongest reading of each network the lamp can name."""
    best = {}
    for entry in results or []:
        try:
            raw = entry[0]
            rssi = int(entry[3])
            auth = int(entry[4])
        except (IndexError, TypeError, ValueError):
            continue
        if isinstance(raw, bytes):
            try:
                ssid = raw.decode("utf-8").strip()
            except UnicodeError:
                continue
        else:
            ssid = str(raw).strip()
        if not ssid or ssid == own_ssid:
            continue
        previous = best.get(ssid)
        if previous is None or rssi > previous["rssi"]:
            best[ssid] = {
                "ssid": ssid,
                "rssi": rssi,
                "auth": auth,
                "kind": network_kind(auth),
            }
    found = list(best.values())
    found.sort(key=lambda item: item["rssi"], reverse=True)
    return found


def parse_profiles(text):
    """Read wifi.dat lines of the form ssid;password."""
    profiles = []
    for line in (text or "").splitlines():
        if ";" not in line:
            continue
        ssid, password = line.split(";", 1)
        ssid = ssid.strip()
        if ssid and not _forbidden(ssid) and not _forbidden(password):
            profiles.append((ssid, password))
    return profiles


def profiles_text(profiles):
    return "".join("{0};{1}\n".format(ssid, password) for ssid, password in profiles)


def _forbidden(text):
    return any(char in text for char in ";\r\n")


def decide_join(networks, ssid, password):
    """Decide what the form is allowed to do. Enterprise networks are refused."""
    ssid = (ssid or "").strip()
    password = password or ""
    if not ssid:
        return "choose", ""
    if _forbidden(ssid) or _forbidden(password):
        return "bad", ""
    chosen = None
    for item in networks:
        if item["ssid"] == ssid:
            chosen = item
            break
    if chosen is None:
        return "unknown", ""
    if chosen["kind"] == "account":
        return "refuse", ""
    if chosen["kind"] == "open":
        return "open", ""
    if password == "":
        return "need_password", ""
    return "join", password


def html_escape(text):
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _page(lang, body):
    words = TEXT[lang]
    other = words["lang_other"]
    return (
        "<!DOCTYPE html><html lang=\"%s\"><head><meta charset=\"utf-8\">"
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">"
        "<title>%s</title></head>"
        "<body style=\"font-family:sans-serif;font-size:18px;line-height:1.4;margin:1.2rem\">"
        "<p><a href=\"/?lang=%s\">%s</a></p>"
        "<h1>%s</h1>%s</body></html>"
    ) % (lang, html_escape(words["title"]), other, html_escape(words["lang_link"]), html_escape(words["title"]), body)


def portal_page(networks, lang):
    words = TEXT[lang if lang in TEXT else "en"]
    lang = lang if lang in TEXT else "en"
    rows = []
    selectable = 0
    for item in networks:
        safe = html_escape(item["ssid"])
        if item["kind"] == "account":
            rows.append("<p><strong>%s</strong><br>%s</p>" % (safe, html_escape(words["account"])))
            continue
        selectable += 1
        note = ""
        if item["kind"] == "open":
            note = "<br>%s" % html_escape(words["open"])
        rows.append(
            "<p><label><input type=\"radio\" name=\"ssid\" value=\"%s\"> %s</label>%s</p>"
            % (safe, safe, note)
        )
    if not rows:
        rows.append("<p>%s</p>" % html_escape(words["none"]))
    password = ""
    if selectable:
        password = (
            "<p><label>%s<br><input name=\"password\" type=\"password\" "
            "autocomplete=\"off\" style=\"font-size:18px;width:18rem\"></label></p>"
            "<p><button type=\"submit\" style=\"font-size:18px;padding:0.6rem 1rem\">%s</button></p>"
        ) % (html_escape(words["password"]), html_escape(words["join"]))
    body = (
        "<p>%s</p><p>%s</p>"
        "<form method=\"post\" action=\"/configure\">"
        "<input type=\"hidden\" name=\"lang\" value=\"%s\">%s%s</form>"
        "<p><a href=\"/scan?lang=%s\">%s</a></p>"
        "<p>%s</p><p>%s</p>"
    ) % (
        html_escape(words["intro"]),
        html_escape(words["only_lamp"]),
        lang,
        "".join(rows),
        password,
        lang,
        html_escape(words["scan"]),
        html_escape(words["hotspot"]),
        html_escape(words["stays"]),
    )
    return _page(lang, body)


def message_page(lang, key, ssid=""):
    words = TEXT[lang if lang in TEXT else "en"]
    lang = lang if lang in TEXT else "en"
    text = words[key].replace("{ssid}", html_escape(ssid))
    body = "<p>%s</p>" % text
    if key != "joined":
        body += "<p><a href=\"/?lang=%s\">%s</a></p>" % (lang, html_escape(words["scan"]))
    return _page(lang, body)


def url_decode(raw):
    if isinstance(raw, str):
        raw = raw.encode("utf-8")
    parts = raw.split(b"%")
    if len(parts) == 1:
        return raw
    out = [parts[0]]
    for item in parts[1:]:
        try:
            out.append(bytes([int(item[:2], 16)]))
            out.append(item[2:])
        except Exception:
            out.append(b"%")
            out.append(item)
    return b"".join(out)


def parse_form(body):
    if isinstance(body, str):
        body = body.encode("utf-8")
    try:
        text = url_decode(body.replace(b"+", b" ")).decode("utf-8")
    except UnicodeError:
        text = ""
    fields = {}
    for pair in text.split("&"):
        if "=" not in pair:
            continue
        key, value = pair.split("=", 1)
        fields[key] = value
    return fields


def request_language(header, query):
    for pair in (query or "").split("&"):
        if pair.startswith("lang="):
            lang = pair.split("=", 1)[1]
            if lang in TEXT:
                return lang
    for line in (header or "").split("\r\n"):
        if line.lower().startswith("accept-language:"):
            value = line.split(":", 1)[1].strip().lower()
            if value.startswith("de"):
                return "de"
    return "en"


def build_dns_response(query, ip=AP_IP):
    """Answer a captive-portal lookup with the lamp's own address."""
    if not query or len(query) < 12 or query[2] & 0x80 or query[4:6] != b"\x00\x01":
        return b""
    ip_bytes = bytes([int(part) for part in ip.split(".")])
    answer = b"\xc0\x0c\x00\x01\x00\x01\x00\x00\x00\x3c\x00\x04" + ip_bytes
    return query[:2] + b"\x81\x80" + b"\x00\x01\x00\x01\x00\x00\x00\x00" + query[12:] + answer


class WifiSetup:
    """Connect with the saved network, or show the phone setup page."""

    def __init__(self, debug=False):
        self.debug = debug
        self.networks = []
        self.wlan_sta = None
        self.wlan_ap = None

    def is_connected(self):
        return bool(self.wlan_sta and self.wlan_sta.isconnected())

    def get_address(self):
        if not self.wlan_sta:
            return None
        return self.wlan_sta.ifconfig()

    def connect(self):
        import network

        self.wlan_sta = network.WLAN(network.STA_IF)
        self.wlan_ap = network.WLAN(network.AP_IF)
        self.wlan_sta.active(True)
        self._disable_power_save()
        if self.wlan_sta.isconnected():
            return
        self.networks = self._scan()
        for ssid, password in self._saved():
            if self._join(ssid, password):
                return
        self._serve()

    def _disable_power_save(self):
        try:
            pm_none = getattr(type(self.wlan_sta), "PM_NONE", 0)
            self.wlan_sta.config(pm=pm_none)
        except Exception as error:
            if self.debug:
                print(error)

    def _saved(self):
        try:
            with open(WIFI_FILE) as handle:
                return parse_profiles(handle.read())
        except OSError:
            return []

    def _write_saved(self, ssid, password):
        with open(WIFI_FILE, "w") as handle:
            handle.write(profiles_text([(ssid, password)]))

    def _scan(self):
        try:
            results = self.wlan_sta.scan() or []
        except OSError as error:
            print("Wi-Fi scan failed:", error)
            return []
        found = parse_scan(results, AP_SSID)
        print("Found networks:", ", ".join(item["ssid"] for item in found) if found else "(none)")
        return found

    def _join(self, ssid, password):
        print("Trying to connect to:", ssid)
        try:
            self.wlan_sta.connect(ssid, password)
        except OSError as error:
            print("Connection failed:", error)
            return False
        for _ in range(100):
            if self.wlan_sta.isconnected():
                print("Connected! Network information:", self.wlan_sta.ifconfig())
                return True
            time.sleep(0.1)
        print("Connection failed!")
        try:
            self.wlan_sta.disconnect()
        except OSError:
            pass
        return False

    def _serve(self):
        import socket

        try:
            machine = __import__("machine")
        except ImportError:
            machine = None
        self._disable_power_save()
        self.wlan_ap.active(True)
        try:
            self.wlan_ap.config(essid=AP_SSID, authmode=0)
            self.wlan_ap.ifconfig((AP_IP, "255.255.255.0", AP_IP, AP_IP))
        except Exception as error:
            print("Access point setup failed:", error)
            return
        dns = None
        try:
            dns = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            dns.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            dns.bind(("0.0.0.0", 53))
            dns.setblocking(False)
        except OSError as error:
            print("DNS portal not started:", error)
            if dns:
                dns.close()
            dns = None
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server.bind(("0.0.0.0", 80))
            server.listen(2)
            server.settimeout(0.2)
        except OSError as error:
            print("Setup page failed:", error)
            server.close()
            if dns:
                dns.close()
            return
        print("Join the Wi-Fi network", AP_SSID + ".")
        print("It has no password. It is only the lamp.")
        print("If the phone does not open a page, go to http://" + AP_IP)
        while True:
            self._service_dns(dns)
            if self.wlan_sta.isconnected():
                self._finish(server, dns, machine)
                return
            try:
                client, _addr = server.accept()
            except OSError:
                continue
            try:
                self._handle(client)
            except Exception as error:
                print("Setup page request failed:", error)
            finally:
                try:
                    client.close()
                except OSError:
                    pass

    def _service_dns(self, dns):
        if dns is None:
            return
        for _ in range(4):
            try:
                query, addr = dns.recvfrom(512)
            except OSError:
                return
            response = build_dns_response(query, AP_IP)
            if not response:
                continue
            try:
                dns.sendto(response, addr)
            except OSError:
                return

    def _finish(self, server, dns, machine):
        time.sleep(8)
        try:
            server.close()
        except OSError:
            pass
        if dns:
            try:
                dns.close()
            except OSError:
                pass
        try:
            self.wlan_ap.active(False)
        except OSError:
            pass
        if machine is not None:
            machine.reset()

    def _read_request(self, client):
        client.settimeout(3)
        data = b""
        try:
            while b"\r\n\r\n" not in data and len(data) < 4096:
                chunk = client.recv(512)
                if not chunk:
                    break
                data += chunk
            if b"\r\n\r\n" not in data:
                return data
            head, _, body = data.partition(b"\r\n\r\n")
            length = 0
            for line in head.split(b"\r\n"):
                if line.lower().startswith(b"content-length:"):
                    try:
                        length = int(line.split(b":", 1)[1].strip())
                    except ValueError:
                        length = 0
            while len(body) < length and len(data) < 8192:
                chunk = client.recv(512)
                if not chunk:
                    break
                data += chunk
                body += chunk
        except OSError:
            pass
        return data

    def _handle(self, client):
        request = self._read_request(client)
        if not request:
            return
        try:
            header = request.decode("utf-8", "replace")
        except Exception:
            return
        first = header.split("\r\n", 1)[0]
        parts = first.split(" ")
        if len(parts) < 2 or parts[0] not in ("GET", "POST"):
            return
        raw = parts[1]
        path, _, query = raw.partition("?")
        if path.startswith("/"):
            path = path[1:]
        path = path.rstrip("/")
        lang = request_language(header, query)
        if path == "favicon.ico":
            self._send(client, b"", 204, "text/plain")
            return
        if parts[0] == "POST" and path == "configure":
            self._configure(client, request, lang)
            return
        if path == "scan":
            self.networks = self._scan()
        self._send(client, portal_page(self.networks, lang))

    def _configure(self, client, request, lang):
        body = request.split(b"\r\n\r\n", 1)[-1] if b"\r\n\r\n" in request else b""
        fields = parse_form(body)
        if fields.get("lang") in TEXT:
            lang = fields["lang"]
        action, password = decide_join(self.networks, fields.get("ssid", ""), fields.get("password", ""))
        ssid = (fields.get("ssid") or "").strip()
        if action in ("choose", "unknown", "bad", "need_password", "refuse"):
            self._send(client, message_page(lang, action, ssid))
            return
        if not self._join(ssid, password):
            self._send(client, message_page(lang, "failed", ssid))
            return
        self._write_saved(ssid, password)
        self._send(client, message_page(lang, "joined", ssid))

    def _send(self, client, body, status=200, content_type="text/html; charset=utf-8"):
        if isinstance(body, str):
            body = body.encode("utf-8")
        reasons = {200: "OK", 204: "No Content", 400: "Bad Request"}
        header = (
            "HTTP/1.1 %d %s\r\n"
            "Content-Type: %s\r\n"
            "Content-Length: %d\r\n"
            "Connection: close\r\n"
            "Cache-Control: no-store\r\n"
            "\r\n"
        ) % (status, reasons.get(status, "OK"), content_type, len(body))
        data = header.encode("ascii") + body
        sent = 0
        while sent < len(data):
            count = client.send(data[sent:])
            if not count:
                break
            sent += count
