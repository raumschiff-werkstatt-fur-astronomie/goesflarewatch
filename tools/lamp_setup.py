#!/usr/bin/env python3
"""Talk to a Solar Flare Alert over the USB cable.

The browser's serial connection holds this lamp in reset and then receives
nothing. This program releases the reset, stops the running program, and
reads or writes the lamp directly. The Wi-Fi password is typed here and
written to the lamp. It is not sent to a server.
"""

import ast
import base64
import getpass
import glob
import json
import os
import sys
import threading
import time
import urllib.request
from pathlib import Path

LEGACY_VERSION = "2025.03"
SITE = "https://raumschiff-werkstatt-fur-astronomie.github.io/goesflarewatch/"
DTR = 0x002
RTS = 0x004

TEXT = {
    "en": {
        "platform": "This program runs on macOS and Linux.",
        "usage": "\n".join(
            [
                "Save lamp_setup.py, open Terminal, and go to the folder where you saved it. Then run one of these commands:",
                "",
                "  python3 lamp_setup.py check",
                "  python3 lamp_setup.py install",
                "  python3 lamp_setup.py wifi",
                "  python3 lamp_setup.py clear",
                "",
                "The check command reads the version from the lamp and reports whether it has joined Wi-Fi. It does not change the program or the saved network.",
                "The install command copies the current Solar Flare Alert onto the lamp. The saved Wi-Fi network is left unchanged.",
                "The wifi command saves a network on the lamp. The password remains on this computer.",
                "The clear command removes the saved Wi-Fi network. The program on the lamp stays as it is.",
            ]
        ),
        "testing": "Testing the lamp. Please wait.",
        "found": "The lamp was found at {port}.",
        "noport": "No lamp was found. Plug the lamp into this computer with a USB cable that carries data, and then try again.",
        "several": "More than one lamp is plugged in. Type the number of the lamp you want to use.",
        "repl": "The lamp did not stop, so the computer could not communicate with it. Unplug the cable, plug it back in, and try again.",
        "raw": "The lamp did not open a connection that the computer can use. Unplug the cable, plug it back in, and try again.",
        "silent": "The lamp sent nothing.",
        "exec": "The lamp did not accept the command. Unplug it, plug it back in, and try again.",
        "device": "The lamp reported an error.",
        "size": "The transfer stopped before it finished. The lamp still has its previous program and its previous Wi-Fi network.",
        "missing": "The Solar Flare Alert program could not be loaded.",
        "busy": "The lamp is already in use. Close any program or page that is using the lamp, and then try again.",
        "current": "This Solar Flare Alert is version {version}, which is the current version.",
        "older": "This Solar Flare Alert is version {version}. Version {latest} is newer. Run install to copy version {latest} onto the lamp.",
        "unknown": "This Solar Flare Alert reports version {version}. The current version is {latest}.",
        "new": "This lamp does not have the Solar Flare Alert program yet. The current version is {latest}. Run install to copy it onto the lamp.",
        "have": "This Solar Flare Alert is version {version}.",
        "catalog": "The list of versions could not be loaded. The number above is the version reported by the lamp.",
        "running": "The lamp is running again. You can unplug the cable.",
        "waiting_wifi": "Waiting to see whether the lamp joins the Wi-Fi network.",
        "wifi_joined": "The lamp is connected to Wi-Fi. You can unplug the cable.",
        "wifi_needed": "The lamp is not connected to Wi-Fi, so the light keeps blinking. Set up the connection by running this command:\n\n  {command}",
        "restarted": "The lamp was restarted. You can unplug the cable.",
        "copying": "Copying the Solar Flare Alert program… {done} / {total}",
        "confirm_install": "This installs Solar Flare Alert {version}. The saved Wi-Fi network is left unchanged, and the external Wi-Fi manager is left unchanged. Continue? [y/N] ",
        "installed": "Solar Flare Alert {version} is on the lamp. The saved Wi-Fi network is unchanged.",
        "install_unseen": "The copy finished and the lamp restarted. The computer did not see the new program start.",
        "looking": "Looking for Wi-Fi networks. Please wait.",
        "networks": "The lamp can see these networks. Type the number of the network it should join.",
        "pick": "Number:",
        "username": "Username:",
        "ssid": "Network name:",
        "password": "Password:",
        "kind_open": "no Wi-Fi password",
        "kind_password": "password",
        "kind_account": "username and password; this lamp cannot join this kind of network",
        "ask_username": "Enter the username. Leave it empty if this network does not use one.",
        "ask_password": "Enter the password. Leave it empty if this network does not use one.",
        "empty_password": "Leave the password empty if the network does not have one.",
        "no_networks": "The lamp did not see any Wi-Fi networks. Move it closer to the access point and try again.",
        "bad_number": "Type the number of a network from the list.",
        "enterprise_no": "{ssid} requires a username and a password when the lamp connects. This lamp cannot join that kind of network. Nothing was saved. Choose a network from the list that uses only a password, or a network with no Wi-Fi password.",
        "open_account": "{ssid} does not use a Wi-Fi password. If a sign-in page asks for an account, enter the username and the password. Leave both empty if it does not ask.",
        "open_unused": "This lamp cannot open a sign-in page, so that account was not saved. The lamp will join the Wi-Fi network.",
        "username_ignored": "This network does not use a username. The password will be saved on the lamp.",
        "need_name": "Enter the network name.",
        "long_name": "The network name must be 32 characters or fewer.",
        "semicolon": "The username and the password cannot contain a semicolon.",
        "private": "The password is written to the lamp over the cable and is not sent to a server.",
        "saving": "Saving the Wi-Fi on the lamp…",
        "connected": "The lamp has joined the Wi-Fi network. You can unplug the cable. The light stops blinking once the connection is established.",
        "rejected": "The lamp did not join that network. Check the network name and the password, and then try again.",
        "wifi_unknown": "The Wi-Fi settings were written to the lamp, and the lamp restarted. If the light stops blinking, the lamp is connected.",
        "confirm_clear": "This removes the Wi-Fi network saved on the lamp. The program on the lamp stays as it is. Continue? [y/N] ",
        "clearing": "Clearing the saved Wi-Fi network…",
        "cleared": "The saved Wi-Fi network has been removed. You can unplug the cable. The light blinks until a new network is saved.",
        "clear_still": "The lamp is still connected to a Wi-Fi network. Unplug the cable, plug it back in, and try again.",
        "clear_unknown": "The saved network was removed and the lamp restarted. If the light is blinking, the Wi-Fi network has been removed.",
        "clear_failed": "The saved Wi-Fi network is still on the lamp.",
        "cancelled": "No changes were made.",
        "details": "Details from the lamp:",
    },
    "de": {
        "platform": "Dieses Programm läuft auf macOS und Linux.",
        "usage": "\n".join(
            [
                "Speichern Sie lamp_setup.py, öffnen Sie das Terminal und wechseln Sie in diesen Ordner. Dann eines davon:",
                "",
                "  python3 lamp_setup.py de check",
                "  python3 lamp_setup.py de install",
                "  python3 lamp_setup.py de wifi",
                "  python3 lamp_setup.py de clear",
                "",
                "check liest die Version. Es ändert das Programm und das WLAN nicht.",
                "install setzt den aktuellen Sonneneruptionsalarm auf die Lampe. Das gespeicherte WLAN bleibt.",
                "wifi speichert ein Netzwerk auf der Lampe. Das Passwort bleibt auf diesem Computer.",
                "clear entfernt das gespeicherte WLAN. Das Programm bleibt, wie es ist.",
            ]
        ),
        "testing": "Die Lampe wird geprüft. Bitte warten.",
        "found": "Der Computer hat die Lampe an {port} gefunden.",
        "noport": "Der Computer hat keine Lampe gefunden. Verbinden Sie sie mit einem USB-Kabel, das Daten überträgt, und versuchen Sie es erneut.",
        "several": "Es ist mehr als eine Lampe angeschlossen. Geben Sie die Nummer dieser Lampe ein.",
        "repl": "Die Lampe hat für den Computer nicht angehalten. Ziehen Sie das Kabel ab, stecken Sie es wieder ein und versuchen Sie es erneut.",
        "raw": "Die Lampe hat keine Verbindung geöffnet, die der Computer nutzen kann. Ziehen Sie das Kabel ab, stecken Sie es wieder ein und versuchen Sie es erneut.",
        "silent": "Die Lampe hat nichts gesendet.",
        "exec": "Die Lampe hat den Befehl nicht angenommen. Ziehen Sie das Kabel ab, stecken Sie es wieder ein und versuchen Sie es erneut.",
        "device": "Die Lampe hat einen Fehler gemeldet.",
        "size": "Die Übertragung ist vorzeitig abgebrochen. Die Lampe hat weiterhin ihr bisheriges Programm und ihr bisheriges WLAN.",
        "missing": "Das Programm des Sonneneruptionsalarms konnte nicht geladen werden.",
        "busy": "Die Lampe wird bereits benutzt. Schliessen Sie das Programm oder die Seite, die mit ihr spricht, und versuchen Sie es erneut.",
        "current": "Dieser Sonneneruptionsalarm hat Version {version}, die aktuelle Version.",
        "older": "Dieser Sonneneruptionsalarm hat Version {version}. {latest} ist neuer. Führen Sie install aus, um {latest} auf die Lampe zu setzen.",
        "unknown": "Dieser Sonneneruptionsalarm meldet {version}. Die aktuelle Version ist {latest}.",
        "new": "Auf dieser Lampe ist das Programm des Sonneneruptionsalarms noch nicht vorhanden. Die aktuelle Version ist {latest}. Führen Sie install aus, um es auf die Lampe zu setzen.",
        "have": "Dieser Sonneneruptionsalarm hat Version {version}.",
        "catalog": "Die Versionsliste konnte nicht geladen werden. Die Zahl oben ist die Meldung der Lampe.",
        "running": "Die Lampe läuft wieder. Sie können das Kabel abziehen.",
        "waiting_wifi": "Es wird geprüft, ob die Lampe eine WLAN-Verbindung aufbaut.",
        "wifi_joined": "Die Lampe ist mit dem WLAN verbunden. Sie können das Kabel abziehen.",
        "wifi_needed": "Die Lampe ist nicht mit dem WLAN verbunden, deshalb blinkt das Licht. Richten Sie die Verbindung ein, indem Sie diesen Befehl ausführen:\n\n  {command}",
        "restarted": "Die Lampe wurde neu gestartet. Sie können das Kabel abziehen.",
        "copying": "Das Programm des Sonneneruptionsalarms wird kopiert … {done} / {total}",
        "confirm_install": "Damit wird Sonneneruptionsalarm {version} installiert. Das gespeicherte WLAN bleibt, wie es ist. Der externe WLAN-Manager bleibt, wie er ist. Fortfahren? [j/N] ",
        "installed": "Sonneneruptionsalarm {version} ist auf der Lampe. Das gespeicherte WLAN ist unverändert.",
        "install_unseen": "Die Kopie ist fertig und die Lampe hat neu gestartet. Der Computer hat das neue Programm nicht erkannt.",
        "looking": "Die WLAN-Netzwerke werden gesucht. Bitte warten.",
        "networks": "Die Lampe sieht diese Netzwerke. Geben Sie die Nummer des Netzwerks ein, mit dem sie sich verbinden soll.",
        "pick": "Nummer:",
        "username": "Benutzername:",
        "ssid": "Netzwerkname:",
        "password": "Passwort:",
        "kind_open": "kein WLAN-Passwort",
        "kind_password": "Passwort",
        "kind_account": "Benutzername und Passwort; die Lampe kann einem solchen Netzwerk nicht beitreten",
        "ask_username": "Geben Sie den Benutzernamen ein. Lassen Sie ihn leer, wenn das Netzwerk keinen benutzt.",
        "ask_password": "Geben Sie das Passwort ein. Lassen Sie es leer, wenn das Netzwerk keines hat.",
        "no_networks": "Die Lampe hat kein WLAN-Netzwerk gesehen. Stellen Sie sie näher an den Zugangspunkt und versuchen Sie es erneut.",
        "bad_number": "Geben Sie die Nummer eines Netzwerks aus der Liste ein.",
        "enterprise_no": "{ssid} verlangt beim Verbinden einen Benutzernamen und ein Passwort. Dieser Art Netzwerk kann die Lampe nicht beitreten. Es wurde nichts gespeichert. Wählen Sie ein Netzwerk, das nur ein Passwort benutzt, oder eines ohne WLAN-Passwort.",
        "open_account": "{ssid} benutzt kein WLAN-Passwort. Wenn eine Anmeldeseite nach einem Konto fragt, geben Sie den Benutzernamen und das Passwort ein. Lassen Sie beides leer, wenn sie nicht danach fragt.",
        "open_unused": "Die Lampe kann keine Anmeldeseite öffnen, deshalb wurde dieses Konto nicht gespeichert. Die Lampe tritt dem WLAN bei.",
        "username_ignored": "Dieses Netzwerk benutzt keinen Benutzernamen. Das Passwort wird auf der Lampe gespeichert.",
        "empty_password": "Das Passwort leer lassen, wenn das Netzwerk keines hat.",
        "need_name": "Geben Sie den Netzwerknamen ein.",
        "long_name": "Der Netzwerkname darf höchstens 32 Zeichen haben.",
        "semicolon": "Netzwerkname und Passwort dürfen kein Semikolon enthalten.",
        "private": "Das Passwort wird über das Kabel auf die Lampe geschrieben. Es wird nicht an einen Server gesendet.",
        "saving": "Das WLAN wird auf der Lampe gespeichert …",
        "connected": "Die Lampe hat sich mit dem WLAN verbunden. Sie können das Kabel abziehen. Wenn das Licht aufhört zu blinken, ist sie verbunden.",
        "rejected": "Die Lampe hat sich nicht mit diesem Netzwerk verbunden. Prüfen Sie Name und Passwort und versuchen Sie es erneut.",
        "wifi_unknown": "Das WLAN wurde auf die Lampe geschrieben, und die Lampe hat neu gestartet. Wenn das Licht aufhört zu blinken, ist sie verbunden.",
        "confirm_clear": "Damit wird das auf der Lampe gespeicherte WLAN entfernt. Das Programm bleibt, wie es ist. Fortfahren? [j/N] ",
        "clearing": "Das gespeicherte WLAN wird gelöscht …",
        "cleared": "Das gespeicherte WLAN ist gelöscht. Sie können das Kabel abziehen. Das Licht blinkt, bis ein neues Netzwerk gespeichert ist.",
        "clear_still": "Die Lampe hat sich trotzdem mit einem WLAN verbunden. Ziehen Sie das Kabel ab, stecken Sie es wieder ein und versuchen Sie es erneut.",
        "clear_unknown": "Das gespeicherte Netzwerk wurde entfernt und die Lampe hat neu gestartet. Wenn das Licht blinkt, ist das WLAN gelöscht.",
        "clear_failed": "Das gespeicherte WLAN ist noch auf der Lampe.",
        "cancelled": "Es wurde nichts geändert.",
        "details": "Meldungen der Lampe:",
    },
}


class LampError(Exception):
    def __init__(self, key, detail=""):
        super().__init__(key)
        self.key = key
        self.detail = detail


class ExecError(Exception):
    def __init__(self, blob):
        super().__init__("exec")
        self.blob = blob


class DeviceError(Exception):
    def __init__(self, blob):
        super().__init__("device")
        self.blob = blob


def _io_numbers():
    if sys.platform == "darwin":
        return 0x4004746A, 0x8004746D, 0x2000740D
    if sys.platform.startswith("linux"):
        return 0x5415, 0x5418, 0x540C
    raise LampError("platform")


def list_ports():
    if sys.platform == "darwin":
        patterns = (
            "/dev/cu.usbserial*",
            "/dev/cu.usbmodem*",
            "/dev/cu.wchusbserial*",
            "/dev/cu.SLAB_USBtoUART*",
        )
    elif sys.platform.startswith("linux"):
        patterns = ("/dev/ttyUSB*", "/dev/ttyACM*")
    else:
        return []
    found = []
    for pattern in patterns:
        found.extend(glob.glob(pattern))
    return sorted(set(found))


def safe_device_name(name):
    stem = name[:-3] if name.endswith(".py") else ""
    if (
        not name.endswith(".py")
        or not stem
        or len(stem) > 40
        or not (stem[0].isalpha() or stem[0] == "_")
        or not all(char.isalnum() or char == "_" for char in stem)
        or name == "wifi_manager.py"
    ):
        raise LampError("missing")
    return name


def safe_relative(relative):
    path = Path(relative)
    if path.is_absolute() or ".." in path.parts or path.name == "wifi_manager.py":
        raise LampError("missing")
    return path


def judge(has_program, version, catalog):
    latest = None
    for item in catalog or []:
        if item.get("latest"):
            latest = item
    if latest is None and catalog:
        latest = catalog[0]
    if not has_program:
        return "new", None, latest
    lamp_version = version or LEGACY_VERSION
    if latest and lamp_version == latest.get("version"):
        return "current", lamp_version, latest
    known = any(item.get("version") == lamp_version for item in catalog or [])
    if known:
        return "older", lamp_version, latest
    return "unknown", lamp_version, latest


def parse_exec(blob):
    if isinstance(blob, str):
        blob = blob.encode("latin-1")
    ok = blob.find(b"OK")
    if ok < 0:
        raise ExecError(blob)
    parts = blob[ok + 2 :].split(b"\x04")
    if len(parts) < 3:
        raise ExecError(blob)
    if parts[1].strip():
        raise DeviceError(parts[1])
    return parts[0].decode("utf-8", "replace")


def parse_lines(text):
    return [line.strip() for line in str(text).replace("\r", "").split("\n") if line.strip()]


def last_flag(lines, yes, no):
    last_yes = last_no = -1
    for index, line in enumerate(lines):
        if line == yes:
            last_yes = index
        elif line == no:
            last_no = index
    return last_yes > last_no


def network_kind(auth):
    if auth in (5, 10):
        return "account"
    if auth in (0, 9):
        return "open"
    return "password"


def parse_scan_output(text):
    best = {}
    for line in parse_lines(text):
        if not line.startswith("NET\t"):
            continue
        parts = line.split("\t")
        if len(parts) != 4:
            continue
        try:
            ssid = ast.literal_eval(parts[1])
            auth = int(parts[2])
            rssi = int(parts[3])
        except (ValueError, SyntaxError):
            continue
        if not isinstance(ssid, str):
            continue
        ssid = ssid.strip()
        if not ssid or ssid == "WifiManager":
            continue
        previous = best.get(ssid)
        if previous is None or rssi > previous["rssi"]:
            best[ssid] = {
                "ssid": ssid,
                "auth": auth,
                "rssi": rssi,
                "kind": network_kind(auth),
            }
    return sorted(best.values(), key=lambda item: item["rssi"], reverse=True)


def scan_networks(lamp):
    reported = lamp.exec_checked(
        "import network\n"
        "station = network.WLAN(network.STA_IF)\n"
        "station.active(True)\n"
        "rows = station.scan() or []\n"
        "for row in rows:\n"
        "    name = row[0].decode()\n"
        "    print('NET\\t' + repr(name) + '\\t' + str(row[4]) + '\\t' + str(row[3]))\n",
        timeout=20,
    )
    return parse_scan_output(reported)


def choose_network(lang, networks):
    print(TEXT[lang]["networks"])
    labels = {
        "open": TEXT[lang]["kind_open"],
        "password": TEXT[lang]["kind_password"],
        "account": TEXT[lang]["kind_account"],
    }
    for index, network in enumerate(networks, 1):
        print("  %d  %s  (%s)" % (index, network["ssid"], labels[network["kind"]]))
    for _attempt in range(2):
        choice = input(TEXT[lang]["pick"] + " ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(networks):
            return networks[int(choice) - 1]
        print(TEXT[lang]["bad_number"])
    raise LampError("bad_number")


def ask_account(lang):
    print(TEXT[lang]["ask_username"])
    username = input(TEXT[lang]["username"] + " ").strip()
    print(TEXT[lang]["ask_password"])
    password = getpass.getpass(TEXT[lang]["password"] + " ")
    if any(char in username or char in password for char in (";", "\n", "\r")):
        raise LampError("semicolon")
    return username, password


def wifi_record(ssid, password):
    if not ssid:
        raise LampError("need_name")
    if len(ssid) > 32:
        raise LampError("long_name")
    if any(char in ssid or char in password for char in (";", "\n", "\r")):
        raise LampError("semicolon")
    return ssid + ";" + password + "\n"


def _decode_detail(blob):
    if isinstance(blob, str):
        blob = blob.encode("latin-1", "replace")
    text = blob.decode("utf-8", "replace").replace("\r", "").strip()
    return text[-2000:]


def load_catalog(source):
    if source:
        root = Path(source)
        catalog = json.loads((root / "versions.json").read_text(encoding="utf-8"))
        files = []
        latest = _latest(catalog)
        for entry in latest["files"]:
            name = safe_device_name(entry["name"])
            relative = safe_relative(entry["file"])
            if relative.name != name:
                raise LampError("missing")
            files.append((name, (root / relative).read_bytes()))
        return catalog, files
    with urllib.request.urlopen(SITE + "versions.json", timeout=30) as response:
        catalog = json.loads(response.read().decode("utf-8"))
    latest = _latest(catalog)
    files = []
    for entry in latest["files"]:
        name = safe_device_name(entry["name"])
        relative = safe_relative(entry["file"])
        if relative.name != name:
            raise LampError("missing")
        with urllib.request.urlopen(SITE + relative.as_posix(), timeout=30) as response:
            files.append((name, response.read()))
    return catalog, files


def _latest(catalog):
    if not isinstance(catalog, list) or not catalog:
        raise LampError("missing")
    latest = [item for item in catalog if item.get("latest") is True]
    if len(latest) != 1:
        raise LampError("missing")
    return latest[0]


class Lamp(object):
    def __init__(self, path):
        self.path = path
        self.fd = None
        self.buffer = b""
        self._lock = threading.Lock()
        self._stop = False
        self._thread = None
        self._get, self._set, self._excl = _io_numbers()

    def open(self):
        try:
            self.fd = os.open(self.path, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
        except OSError as error:
            if getattr(error, "errno", None) == 16:
                raise LampError("busy")
            raise
        try:
            self._configure()
            self._stop = False
            self._thread = threading.Thread(target=self._read_loop, daemon=True)
            self._thread.start()
            time.sleep(0.05)
            self.set_line(DTR, False)
            time.sleep(0.05)
            self.set_line(RTS, False)
            time.sleep(0.1)
        except Exception:
            self.close()
            raise

    def _configure(self):
        import fcntl
        import termios

        try:
            fcntl.ioctl(self.fd, self._excl)
        except OSError:
            pass
        attrs = termios.tcgetattr(self.fd)
        attrs[0] = 0
        attrs[1] = 0
        attrs[2] = (attrs[2] | termios.CLOCAL | termios.CREAD) & ~termios.HUPCL
        attrs[3] = 0
        attrs[4] = termios.B115200
        attrs[5] = termios.B115200
        attrs[6][termios.VMIN] = 1
        attrs[6][termios.VTIME] = 0
        termios.tcsetattr(self.fd, termios.TCSANOW, attrs)
        termios.tcflush(self.fd, termios.TCIOFLUSH)

    def set_line(self, mask, on):
        import ctypes
        import fcntl

        state = ctypes.c_int()
        fcntl.ioctl(self.fd, self._get, state)
        state.value = (state.value | mask) if on else (state.value & ~mask)
        fcntl.ioctl(self.fd, self._set, state)

    def _read_loop(self):
        while not self._stop:
            try:
                chunk = os.read(self.fd, 8192)
            except BlockingIOError:
                time.sleep(0.02)
                continue
            except OSError:
                return
            if not chunk:
                time.sleep(0.02)
                continue
            with self._lock:
                self.buffer += chunk
                if len(self.buffer) > 200000:
                    self.buffer = self.buffer[-100000:]

    def since(self, mark):
        with self._lock:
            return self.buffer[mark:]

    def mark(self):
        with self._lock:
            return len(self.buffer)

    def _write(self, data):
        if isinstance(data, str):
            data = data.encode("utf-8")
        while data:
            try:
                written = os.write(self.fd, data)
            except BlockingIOError:
                time.sleep(0.01)
                continue
            if written <= 0:
                raise LampError("exec")
            data = data[written:]

    def interrupt(self):
        mark = self.mark()
        deadline = time.monotonic() + 8
        while time.monotonic() < deadline:
            self._write(b"\r\x03\x03")
            time.sleep(0.2)
            if b">>>" in self.since(mark):
                time.sleep(0.15)
                return True
        return False

    def reboot(self):
        # RTS asserted holds this board in reset. DTR stays released so it
        # boots the program instead of the serial loader.
        self.set_line(RTS, True)
        time.sleep(0.12)
        self.set_line(DTR, False)
        self.set_line(RTS, False)
        time.sleep(0.15)

    def enter_raw(self):
        mark = self.mark()
        self._write(b"\r\x01")
        deadline = time.monotonic() + 4
        while time.monotonic() < deadline:
            if b"raw REPL; CTRL-B to exit" in self.since(mark):
                time.sleep(0.2)
                return
            time.sleep(0.03)
        raise LampError("raw", _decode_detail(self.since(mark)))

    def prepare(self):
        if not self.interrupt():
            self.reboot()
            if not self.interrupt():
                captured = self.since(0)
                if captured.strip():
                    raise LampError("repl", _decode_detail(captured))
                raise LampError("silent")
        self.enter_raw()

    def exec(self, code, timeout=10):
        if not str(code).strip():
            raise LampError("exec")
        payload = code.encode("utf-8") if isinstance(code, str) else bytes(code)
        mark = self.mark()
        for offset in range(0, len(payload), 128):
            self._write(payload[offset : offset + 128])
            time.sleep(0.015)
        self._write(b"\x04")
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            blob = self.since(mark)
            try:
                return parse_exec(blob)
            except DeviceError:
                raise
            except ExecError:
                time.sleep(0.02)
        raise ExecError(self.since(mark))

    def exec_checked(self, code, timeout=15):
        try:
            return self.exec(code, timeout)
        except ExecError:
            self.enter_raw()
            return self.exec(code, timeout)

    def restart(self):
        mark = self.mark()
        self.reboot()
        deadline = time.monotonic() + 2
        while time.monotonic() < deadline:
            text = self.since(mark)
            if b"ets " in text or b"MicroPython" in text or b"rst:" in text:
                return True
            time.sleep(0.05)
        return False

    def close(self):
        self._stop = True
        fd = self.fd
        self.fd = None
        if fd is not None:
            try:
                os.close(fd)
            except OSError:
                pass
        if self._thread is not None:
            self._thread.join(timeout=1)
            self._thread = None


def read_state(lamp):
    reported = lamp.exec_checked(
        "import os\n"
        "names = os.listdir()\n"
        "print('yes' if 'solar_flare_alert.py' in names else 'no')\n"
        "print('file' if 'version.py' in names else 'none')\n"
    )
    lines = parse_lines(reported)
    has_program = last_flag(lines, "yes", "no")
    version = None
    if last_flag(lines, "file", "none"):
        numbered = lamp.exec_checked("import version\nprint(version.VERSION)\n")
        parts = parse_lines(numbered)
        version = parts[-1] if parts else None
        if version == "none":
            version = None
    return has_program, version


def write_program_file(lamp, name, file_bytes, on_progress=None):
    safe = safe_device_name(name)
    temp = safe + ".new"
    lamp.exec_checked(
        "import os\n"
        "try:\n"
        "    os.remove(%r)\n"
        "except OSError:\n"
        "    pass\n"
        "f = open(%r, 'wb')\n" % (temp, temp)
    )
    total = len(file_bytes)
    done = 0
    for offset in range(0, total or 1, 240):
        if total == 0:
            break
        piece = file_bytes[offset : offset + 240]
        encoded = base64.b64encode(piece).decode("ascii")
        lamp.exec_checked("f.write(__import__('ubinascii').a2b_base64('%s'))\n" % encoded)
        done += len(piece)
        if on_progress:
            on_progress(done, total)
    lamp.exec_checked("f.close()\n")
    reported = lamp.exec_checked("import os\nprint(os.stat(%r)[6])\n" % temp)
    lines = parse_lines(reported)
    if not lines or int(lines[-1]) != total:
        try:
            lamp.exec_checked("import os\nos.remove(%r)\n" % temp)
        except (ExecError, DeviceError, LampError):
            pass
        raise LampError("size")
    lamp.exec_checked(
        "import os\n"
        "try:\n"
        "    os.remove(%r)\n"
        "except OSError:\n"
        "    pass\n"
        "os.rename(%r, %r)\n" % (safe, temp, safe)
    )


def save_wifi(lamp, record):
    encoded = base64.b64encode(record.encode("utf-8")).decode("ascii")
    reported = lamp.exec_checked(
        "f = open('wifi.dat', 'w')\n"
        "f.write(__import__('ubinascii').a2b_base64('%s').decode())\n"
        "f.close()\n"
        "print(len(open('wifi.dat').read()))\n" % encoded
    )
    lines = parse_lines(reported)
    if not lines or int(lines[-1]) != len(record):
        raise LampError("size")


def clear_wifi(lamp):
    reported = lamp.exec_checked(
        "import os\n"
        "try:\n"
        "    os.remove('wifi.dat')\n"
        "except OSError:\n"
        "    pass\n"
        "print('gone' if 'wifi.dat' not in os.listdir() else 'kept')\n"
    )
    if not last_flag(parse_lines(reported), "gone", "kept"):
        raise LampError("clear_failed")


def watch(lamp, decide, seconds):
    mark = lamp.mark()
    lamp.reboot()
    lamp.booted = True
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        text = lamp.since(mark).decode("utf-8", "replace")
        result = decide(text)
        if result:
            return result
        time.sleep(0.15)
    return None


def connection_result(text):
    if "Connected!" in text or "Connected to Wi-Fi!" in text:
        return "connected"
    if (
        "Could not connect" in text
        or "configuration portal" in text
        or "Starting the configuration portal" in text
        or "sign-in page" in text
        or "Join the open" in text
        or "Join Wi-Fi network" in text
    ):
        return "offline"
    return None


def wifi_result(text):
    if "Traceback" in text:
        return "error"
    if "Connected!" in text:
        return "connected"
    if (
        "Connection failed" in text
        or "sign-in page" in text
        or "Join the open" in text
        or "with the password" in text
    ):
        return "rejected"
    if "Could not connect" in text and "portal" in text:
        return "rejected"
    return None


def reset_result(text):
    if "Traceback" in text:
        return "error"
    if "Connected!" in text:
        return "still"
    if (
        "configuration portal" in text
        or "sign-in page" in text
        or "Join the open" in text
        or "with the password" in text
        or "Could not connect" in text
    ):
        return "cleared"
    return None


def program_result(version):
    needle = "Solar Flare Alert " + version

    def decide(text):
        if "Traceback" in text:
            return "error"
        if needle in text:
            return "updated"
        return None

    return decide


def choose_port(lang):
    ports = list_ports()
    if not ports:
        raise LampError("noport")
    if len(ports) == 1:
        return ports[0]
    print(TEXT[lang]["several"])
    for index, port in enumerate(ports, 1):
        print("%d  %s" % (index, port))
    choice = input("> ").strip()
    if not choice.isdigit() or not 1 <= int(choice) <= len(ports):
        raise LampError("noport")
    return ports[int(choice) - 1]


def with_lamp(lang, work):
    port = choose_port(lang)
    print(TEXT[lang]["found"].format(port=port), flush=True)
    lamp = Lamp(port)
    lamp.booted = False
    lamp.open()
    running = False
    try:
        lamp.prepare()
        return work(lamp)
    finally:
        try:
            if lamp.booted:
                running = True
            else:
                running = lamp.restart()
        except Exception:
            running = False
        lamp.close()
        if not getattr(lamp, "explained", False):
            print(TEXT[lang]["running"] if running else TEXT[lang]["restarted"], flush=True)


def confirmed(lang, key, **values):
    answer = input(TEXT[lang][key].format(**values)).strip().lower()
    return answer in ("y", "yes", "j", "ja")


def describe_version(lang, has_program, version, catalog, catalog_ok):
    status, lamp_version, latest_item = judge(has_program, version, catalog)
    latest_name = latest_item.get("version") if latest_item else ""
    if status == "current":
        print(TEXT[lang]["current"].format(version=lamp_version))
    elif status == "new":
        print(TEXT[lang]["new"].format(latest=latest_name or LEGACY_VERSION))
    elif status == "older":
        print(TEXT[lang]["older"].format(version=lamp_version, latest=latest_name))
    elif status == "unknown" and latest_name:
        print(TEXT[lang]["unknown"].format(version=lamp_version, latest=latest_name))
    else:
        print(TEXT[lang]["have"].format(version=lamp_version or LEGACY_VERSION))
    if not catalog_ok:
        print(TEXT[lang]["catalog"])


def report_version(lang, source):
    print(TEXT[lang]["testing"], flush=True)
    try:
        catalog, _files = load_catalog(source)
        catalog_ok = True
    except Exception:
        catalog = []
        catalog_ok = False

    def work(lamp):
        has_program, version = read_state(lamp)
        describe_version(lang, has_program, version, catalog, catalog_ok)
        if not has_program:
            return
        print(TEXT[lang]["waiting_wifi"], flush=True)
        outcome = watch(lamp, connection_result, 40)
        command = "python3 lamp_setup.py wifi" if lang == "en" else "python3 lamp_setup.py de wifi"
        if outcome == "connected":
            print(TEXT[lang]["wifi_joined"], flush=True)
        else:
            print(TEXT[lang]["wifi_needed"].format(command=command), flush=True)
        lamp.explained = True

    with_lamp(lang, work)
    return 0


def install_program(lang, source):
    try:
        catalog, files = load_catalog(source)
        latest = _latest(catalog)
    except LampError:
        raise
    except Exception:
        raise LampError("missing")
    version = latest["version"]
    if not confirmed(lang, "confirm_install", version=version):
        print(TEXT[lang]["cancelled"])
        return 0
    total = sum(len(data) for _name, data in files)
    copied = [0]

    def copy(lamp):
        for name, data in files:
            def progress(done, _total, name=name):
                print(
                    TEXT[lang]["copying"].format(done=copied[0] + done, total=total),
                    flush=True,
                )

            write_program_file(lamp, name, data, progress)
            copied[0] += len(data)
        seen = watch(lamp, program_result(version), 25)
        return seen

    seen = with_lamp(lang, copy)
    if seen == "updated":
        print(TEXT[lang]["installed"].format(version=version))
        return 0
    print(TEXT[lang]["install_unseen"])
    return 0


def save_network(lang):
    print(TEXT[lang]["looking"], flush=True)
    port = choose_port(lang)
    print(TEXT[lang]["found"].format(port=port), flush=True)
    lamp = Lamp(port)
    lamp.booted = False
    lamp.open()
    try:
        lamp.prepare()
        networks = scan_networks(lamp)
        if not networks:
            print(TEXT[lang]["no_networks"])
            return 1
        chosen = choose_network(lang, networks)
        if chosen["kind"] == "account":
            print(TEXT[lang]["enterprise_no"].format(ssid=chosen["ssid"]))
            return 1
        if chosen["kind"] == "open":
            print(TEXT[lang]["open_account"].format(ssid=chosen["ssid"]))
        username, password = ask_account(lang)
        if chosen["kind"] == "open":
            if username or password:
                print(TEXT[lang]["open_unused"])
            record = wifi_record(chosen["ssid"], "")
        else:
            if username:
                print(TEXT[lang]["username_ignored"])
            record = wifi_record(chosen["ssid"], password)
        print(TEXT[lang]["private"], flush=True)
        print(TEXT[lang]["saving"], flush=True)
        save_wifi(lamp, record)
        result = watch(lamp, wifi_result, 25)
    finally:
        try:
            if not lamp.booted:
                lamp.restart()
        except Exception:
            pass
        lamp.close()
    if result == "connected":
        print(TEXT[lang]["connected"])
        return 0
    if result == "rejected" or result == "error":
        print(TEXT[lang]["rejected"])
        return 1
    print(TEXT[lang]["wifi_unknown"])
    return 0


def clear_network(lang):
    if not confirmed(lang, "confirm_clear"):
        print(TEXT[lang]["cancelled"])
        return 0

    def work(lamp):
        print(TEXT[lang]["clearing"], flush=True)
        clear_wifi(lamp)
        return watch(lamp, reset_result, 25)

    result = with_lamp(lang, work)
    if result == "cleared":
        print(TEXT[lang]["cleared"])
    elif result == "still":
        print(TEXT[lang]["clear_still"])
        return 1
    else:
        print(TEXT[lang]["clear_unknown"])
    return 0


def parse_args(argv):
    lang = "de" if os.environ.get("LANG", "").lower().startswith("de") else "en"
    source = None
    command = ""
    args = list(argv[1:])
    if args and args[0] in ("de", "en"):
        lang = args.pop(0)
    index = 0
    kept = []
    while index < len(args):
        if args[index] == "--source" and index + 1 < len(args):
            source = args[index + 1]
            index += 2
            continue
        kept.append(args[index])
        index += 1
    if kept:
        command = kept[0]
    return lang, source, command


def main(argv=None):
    argv = list(sys.argv if argv is None else argv)
    lang, source, command = parse_args(argv)
    if command not in ("check", "install", "wifi", "clear"):
        print(TEXT[lang]["usage"])
        return 2
    if sys.platform != "darwin" and not sys.platform.startswith("linux"):
        print(TEXT[lang]["platform"])
        return 2
    try:
        if command == "check":
            return report_version(lang, source)
        if command == "install":
            return install_program(lang, source)
        if command == "wifi":
            return save_network(lang)
        return clear_network(lang)
    except LampError as error:
        print(TEXT[lang].get(error.key, TEXT[lang]["exec"]))
        if error.detail:
            print(TEXT[lang]["details"])
            print(error.detail)
        return 1
    except DeviceError as error:
        print(TEXT[lang]["device"])
        print(TEXT[lang]["details"])
        print(_decode_detail(error.blob))
        return 1
    except ExecError as error:
        print(TEXT[lang]["exec"])
        detail = _decode_detail(error.blob)
        if detail:
            print(TEXT[lang]["details"])
            print(detail)
        return 1
    except KeyboardInterrupt:
        print("")
        return 1


if __name__ == "__main__":
    sys.exit(main())
