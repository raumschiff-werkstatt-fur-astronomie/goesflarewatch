(function () {
  function sleep(ms) {
    return new Promise(function (resolve) {
      setTimeout(resolve, ms);
    });
  }

  function bytesToBase64(bytes) {
    var binary = "";
    for (var i = 0; i < bytes.length; i++) {
      binary += String.fromCharCode(bytes[i]);
    }
    return btoa(binary);
  }

  function LampPort(port) {
    this.port = port;
    this.buffer = "";
    this.mark = 0;
    this.reader = null;
    this.writer = null;
    this.reading = false;
    this.readError = null;
  }

  LampPort.prototype.open = async function () {
    // The boot text is 348 bytes. The browser default buffer is 255, so the
    // port errors before the lamp can answer, and the details stay empty.
    await this.port.open({ baudRate: 115200, bufferSize: 65536 });
    // Opening the port asserts both control lines. On this lamp that holds the
    // processor in reset, so it sends nothing until the lines are released.
    await this.hardReset(false);
    this.writer = this.port.writable.getWriter();
    this.reader = this.port.readable.getReader();
    this.reading = true;
    this._readLoop();
  };

  LampPort.prototype._readLoop = async function () {
    var decoder = new TextDecoder();
    try {
      while (this.reading) {
        var result = await this.reader.read();
        if (result.done) break;
        if (result.value) {
          this.buffer += decoder.decode(result.value, { stream: true });
          if (this.buffer.length > 16000) {
            var drop = this.buffer.length - 8000;
            this.buffer = this.buffer.slice(drop);
            this.mark = Math.max(0, this.mark - drop);
          }
          this.note();
        }
      }
    } catch (error) {
      error.captured = this.buffer.slice(-4000);
      this.readError = error;
      this.note();
    }
  };

  LampPort.prototype.note = function () {
    if (this.onText) this.onText(this.buffer.slice(-4000));
  };

  LampPort.prototype.fail = function (error) {
    if (!error.captured) error.captured = this.buffer.slice(-4000);
    throw error;
  };

  LampPort.prototype.since = function () {
    return this.buffer.slice(this.mark);
  };

  LampPort.prototype.writeBytes = async function (bytes) {
    if (this.readError) this.fail(this.readError);
    try {
      await this.writer.write(bytes);
    } catch (error) {
      this.fail(error);
    }
  };

  LampPort.prototype.hardReset = async function (inverted) {
    this.mark = this.buffer.length;
    if (inverted) {
      await this.port.setSignals({ dataTerminalReady: true, requestToSend: false });
      await sleep(120);
      await this.port.setSignals({ dataTerminalReady: false, requestToSend: false });
    } else {
      await this.port.setSignals({ dataTerminalReady: false, requestToSend: true });
      await sleep(120);
      await this.port.setSignals({ dataTerminalReady: false, requestToSend: false });
    }
    await sleep(30);
  };

  LampPort.prototype.interrupt = async function () {
    var deadline = Date.now() + 12000;
    while (Date.now() < deadline) {
      await this.writeBytes(new Uint8Array([13, 3, 3]));
      var look = Date.now() + 200;
      while (Date.now() < look) {
        if (this.readError) this.fail(this.readError);
        if (this.since().indexOf(">>>") !== -1) {
          await sleep(150);
          return true;
        }
        await sleep(40);
      }
    }
    return false;
  };

  LampPort.prototype.enterRaw = async function () {
    this.mark = this.buffer.length;
    await this.writeBytes(new Uint8Array([13, 1]));
    var banner = await this.waitFor("raw REPL; CTRL-B to exit", 4000);
    if (banner.indexOf("raw REPL; CTRL-B to exit") === -1) {
      var raw = new Error("raw");
      raw.captured = banner;
      throw raw;
    }
    await sleep(200);
  };

  LampPort.prototype.prepare = async function () {
    var ready = await this.interrupt();
    if (!ready) {
      await this.hardReset(false);
      ready = await this.interrupt();
    }
    if (!ready) {
      var missed = new Error("repl");
      missed.captured = this.buffer.slice(-4000);
      throw missed;
    }
    await this.enterRaw();
  };

  LampPort.prototype.waitFor = async function (needle, timeout) {
    var deadline = Date.now() + timeout;
    while (Date.now() < deadline) {
      if (this.since().indexOf(needle) !== -1) return this.since();
      if (this.readError) throw this.readError;
      await sleep(30);
    }
    return this.since();
  };

  LampPort.prototype.execRaw = async function (code, timeout) {
    var start = this.buffer.length;
    var data = new TextEncoder().encode(code);
    for (var i = 0; i < data.length; i += 128) {
      await this.writeBytes(data.subarray(i, Math.min(i + 128, data.length)));
      await sleep(15);
    }
    await this.writeBytes(new Uint8Array([4]));
    var deadline = Date.now() + (timeout || 8000);
    var slice = "";
    while (Date.now() < deadline) {
      slice = this.buffer.slice(start);
      if (slice.indexOf("OK") !== -1 && slice.split("\u0004").length - 1 >= 2) break;
      if (this.readError) throw this.readError;
      await sleep(20);
    }
    slice = this.buffer.slice(start);
    if (slice.indexOf("OK") === -1 || slice.split("\u0004").length - 1 < 2) {
      if (this.readError) this.fail(this.readError);
      var failed = new Error("exec");
      failed.captured = slice || this.buffer.slice(-4000);
      throw failed;
    }
    var rest = slice.slice(slice.indexOf("OK") + 2);
    var parts = rest.split("\u0004");
    if ((parts[1] || "").trim()) {
      var device = new Error("device");
      device.detail = parts[1].trim();
      device.captured = slice;
      throw device;
    }
    return parts[0];
  };

  LampPort.prototype.watch = async function (decide) {
    await this.hardReset(false);
    var deadline = Date.now() + 25000;
    while (Date.now() < deadline) {
      var result = decide(this.since());
      if (result) return { result: result, text: this.since() };
      await sleep(150);
    }
    return { result: "unknown", text: this.since() };
  };

  LampPort.prototype.close = async function () {
    this.reading = false;
    try {
      await this.port.setSignals({ dataTerminalReady: false, requestToSend: false });
    } catch (error) {
      /* The cable may already be gone. */
    }
    try {
      await this.reader.cancel();
    } catch (error) {
      /* Already closed. */
    }
    try {
      this.reader.releaseLock();
    } catch (error) {
      /* Already released. */
    }
    try {
      this.writer.releaseLock();
    } catch (error) {
      /* Already released. */
    }
    try {
      await this.port.close();
    } catch (error) {
      /* Already closed. */
    }
  };

  async function saveWifi(lamp, ssid, password) {
    var line = ssid + ";" + password + "\n";
    var encoded = bytesToBase64(new TextEncoder().encode(line));
    var reported = await lamp.execRaw(
      "f = open('wifi.dat','w')\n" +
        "f.write(__import__('ubinascii').a2b_base64('" +
        encoded +
        "').decode())\n" +
        "f.close()\n" +
        "print(len(open('wifi.dat').read()))\n"
    );
    if (parseInt(String(reported).trim(), 10) !== line.length) {
      throw new Error("size");
    }
  }

  async function clearWifi(lamp) {
    var reported = await lamp.execRaw(
      "import os\n" +
        "try:\n" +
        "    os.remove('wifi.dat')\n" +
        "except OSError:\n" +
        "    pass\n" +
        "print('gone' if 'wifi.dat' not in os.listdir() else 'kept')\n"
    );
    if (String(reported).indexOf("gone") === -1) {
      throw new Error("wifiResetFailed");
    }
  }

  function resetResult(text) {
    if (text.indexOf("Traceback") !== -1) return "error";
    if (text.indexOf("Connected!") !== -1) return "still";
    if (
      text.indexOf("configuration portal") !== -1 ||
      text.indexOf("sign-in page") !== -1 ||
      text.indexOf("Join the open") !== -1 ||
      text.indexOf("with the password") !== -1 ||
      text.indexOf("Could not connect") !== -1
    ) {
      return "cleared";
    }
    return null;
  }

  function safeDeviceName(name) {
    if (!/^[A-Za-z_][A-Za-z0-9_]{0,40}\.py$/.test(name)) throw new Error("missing-file");
    if (name === "wifi_manager.py") throw new Error("missing-file");
    return name;
  }

  async function writeProgramFile(lamp, name, fileBytes, onProgress) {
    var safe = safeDeviceName(name);
    var temp = safe + ".new";
    await lamp.execRaw("f = open('" + temp + "','wb')");
    var chunk = 240;
    for (var offset = 0; offset < fileBytes.length; offset += chunk) {
      var piece = fileBytes.subarray(offset, Math.min(offset + chunk, fileBytes.length));
      var encoded = bytesToBase64(piece);
      await lamp.execRaw("f.write(__import__('ubinascii').a2b_base64('" + encoded + "'))");
      if (onProgress) onProgress(Math.min(offset + chunk, fileBytes.length), fileBytes.length);
    }
    await lamp.execRaw("f.close()");
    var reported = await lamp.execRaw("import os\nprint(os.stat('" + temp + "')[6])");
    if (parseInt(String(reported).trim(), 10) !== fileBytes.length) {
      try {
        await lamp.execRaw("import os\nos.remove('" + temp + "')");
      } catch (error) {
        /* The partial file is unused. The lamp still has its previous program. */
      }
      throw new Error("size");
    }
    await lamp.execRaw(
      "import os\n" +
        "try:\n" +
        "    os.remove('" + safe + "')\n" +
        "except OSError:\n" +
        "    pass\n" +
        "os.rename('" + temp + "','" + safe + "')\n"
    );
  }

  var LEGACY_VERSION = "2025.03";

  async function execChecked(lamp, code) {
    try {
      return await lamp.execRaw(code, 15000);
    } catch (error) {
      if (error.message !== "exec") throw error;
      await lamp.enterRaw();
      return await lamp.execRaw(code, 15000);
    }
  }

  async function readLampState(lamp) {
    var reported = await execChecked(
      lamp,
      "import os\n" +
        "names = os.listdir()\n" +
        "print('yes' if 'solar_flare_alert.py' in names else 'no')\n" +
        "print('file' if 'version.py' in names else 'none')\n"
    );
    var lines = String(reported)
      .replace(/\r/g, "")
      .split("\n")
      .map(function (line) {
        return line.trim();
      })
      .filter(Boolean);
    var hasProgram = lines.lastIndexOf("yes") > lines.lastIndexOf("no");
    var version = null;
    if (lines.lastIndexOf("file") > lines.lastIndexOf("none")) {
      var numbered = await execChecked(lamp, "import version\nprint(version.VERSION)\n");
      version = String(numbered).trim().split(/\s+/).pop();
      if (!version || version === "none") version = null;
    }
    return { hasProgram: hasProgram, version: version };
  }

  function judgeVersion(state, catalog) {
    var latest = null;
    for (var i = 0; i < catalog.length; i++) {
      if (catalog[i].latest) latest = catalog[i];
    }
    if (!latest && catalog.length) latest = catalog[0];
    if (!state || !state.hasProgram) return { status: "new", version: null, latest: latest };
    var lampVersion = state.version || LEGACY_VERSION;
    if (latest && lampVersion === latest.version) {
      return { status: "current", version: lampVersion, latest: latest };
    }
    var known = false;
    for (var j = 0; j < catalog.length; j++) {
      if (catalog[j].version === lampVersion) known = true;
    }
    if (known) return { status: "older", version: lampVersion, latest: latest };
    return { status: "unknown", version: lampVersion, latest: latest };
  }

  function wifiResult(text) {
    if (text.indexOf("Traceback") !== -1) return "error";
    if (text.indexOf("Connected!") !== -1) return "connected";
    if (
      text.indexOf("Connection failed") !== -1 ||
      text.indexOf("sign-in page") !== -1 ||
      text.indexOf("Join the open") !== -1 ||
      text.indexOf("with the password") !== -1
    ) {
      return "rejected";
    }
    if (text.indexOf("Could not connect") !== -1 && text.indexOf("portal") !== -1) return "rejected";
    return null;
  }

  function programResult(version) {
    return function (text) {
      if (text.indexOf("Traceback") !== -1) return "error";
      if (text.indexOf("Solar Flare Alert " + version) !== -1) return "updated";
      return null;
    };
  }

  var copy = {
    en: {
      language: "Deutsch",
      browser: "This browser cannot reach the lamp over USB. Open this page in Firefox, Chrome, or Edge on the computer. Safari cannot.",
      cable: "Plug the lamp into this computer with a data USB cable.",
      working: "Restarting the lamp…",
      talking: "The lamp is listening.",
      repl: "The lamp did not stop for the computer. Unplug it, plug it back in, and try again.",
      raw: "The lamp did not open a connection the computer can use. Unplug it, plug it back in, and try again.",
      silent: "The lamp sent nothing.",
      exec: "The lamp did not accept the command. Unplug it, plug it back in, and try again.",
      device: "The lamp reported an error. The details are below.",
      size: "The transfer stopped early. The lamp still has its previous program and its previous Wi-Fi.",
      cancel: "No lamp was selected.",
      missing: "This page could not load the Solar Flare Alert program.",
      serialLog: "Details from the lamp",
      homeTitle: "Solar Flare Alert",
      homeWifi: "Set up Wi-Fi for the Solar Flare Alert",
      homeWifiBody: "Saves the network name and password on the lamp. The program on the lamp stays as it is.",
      homeUpgrade: "Solar Flare Alert versions",
      homeUpgradeBody: "Versions of the Solar Flare Alert. Check the lamp to see if a newer one is published. The saved Wi-Fi stays as it is.",
      wifiTitle: "Set up Wi-Fi for the Solar Flare Alert",
      wifiLead: "Plug the lamp into this computer with a data USB cable. This page saves the Wi-Fi on the lamp. It does not change the program.",
      wifiPrivate: "The password is written to the lamp over the cable. This page does not send it to a server.",
      ssid: "Network name",
      password: "Password",
      emptyPassword: "Leave this empty when the network has no password.",
      show: "Show password",
      wifiButton: "Connect the lamp and save the Wi-Fi",
      wifiReset: "The Wi-Fi is already set. Clear it.",
      wifiResetLead: "This removes the Wi-Fi saved on the Solar Flare Alert. The lamp forgets that network. The program stays as it is.",
      wifiResetChoose: "Choose the lamp and clear the Wi-Fi",
      wifiResetBack: "Type a network instead.",
      wifiResetting: "Clearing the saved Wi-Fi…",
      wifiResetDone: "The saved Wi-Fi is gone. You can unplug the cable. The light blinks until a new network is saved.",
      wifiResetStill: "The lamp still joined a Wi-Fi. Unplug it, plug it back in, and try again.",
      wifiResetUnknown: "The saved network was removed and the lamp restarted. If the light is blinking, the Wi-Fi is cleared.",
      wifiResetFailed: "The saved Wi-Fi is still on the lamp. Unplug it, plug it back in, and try again.",
      wifiNeedName: "Enter the network name.",
      wifiSemicolon: "The network name and the password cannot contain a semicolon.",
      wifiLong: "The network name has to be 32 characters or fewer.",
      wifiSaving: "Saving the Wi-Fi on the lamp…",
      stepCount: "Step {n} of {total}",
      wifiStep1: "Plug the Solar Flare Alert into this computer with a USB cable that carries data. Wait until the light is blinking.",
      wifiNextPlug: "The light is blinking",
      wifiNotBlinking: "The light is not blinking",
      wifiRunning: "The light is not blinking because the Solar Flare Alert is already running. It has already joined a Wi-Fi network. You can leave it as it is, or save a different network.",
      wifiLeave: "Leave it as it is",
      wifiReplace: "Save a different network",
      wifiSteady: "You can unplug the cable. The lamp keeps the Wi-Fi it already has.",
      wifiStep2: "Type the Wi-Fi network this lamp should join.",
      wifiNextNet: "Continue",
      wifiStep3: "Next, the browser asks which device to allow. Choose the lamp. It may be named USB Serial, CP2102, or USB JTAG.",
      wifiChoose: "Choose the lamp",
      wifiAgain: "Start again",
      wifiConnected: "The lamp has joined the Wi-Fi. You can unplug the cable. When the light stops blinking, it is connected.",
      wifiRejected: "The lamp did not join that network. Check the name and the password, then try again.",
      wifiUnknown: "The Wi-Fi was written to the lamp, and the lamp restarted. If the light stops blinking, it is connected.",
      upgradeTitle: "Solar Flare Alert versions",
      checkLamp: "Check this lamp",
      checkStep1: "Plug the Solar Flare Alert into this computer with a USB cable that carries data.",
      checkNextPlug: "The lamp is plugged in",
      checkWorking: "Testing the lamp. Please wait.",
      checkStep2: "This reads the version from the lamp. It does not change the program or the Wi-Fi. Next, the browser asks which device to allow. Choose the lamp. It may be named USB Serial, CP2102, or USB JTAG.",
      checkChoose: "Choose the lamp and check",
      checkCurrent: "This Solar Flare Alert is {version}, the latest version on this page.",
      checkOlder: "This Solar Flare Alert is {version}. {latest} is newer.",
      checkUnrecorded: "This Solar Flare Alert has no version recorded. The latest on this page is {latest}.",
      checkUnknown: "This Solar Flare Alert reports {version}. That version is not listed here. The latest on this page is {latest}.",
      checkNew: "This lamp does not have the Solar Flare Alert program yet. The latest on this page is {latest}.",
      latest: "Latest",
      allVersions: "All versions",
      install: "Install",
      upgradeBack: "All versions",
      upgradeStep1: "Plug the Solar Flare Alert into this computer with a USB cable that carries data. Wait until the light is blinking.",
      upgradeNextPlug: "The light is blinking",
      upgradeInstalling: "This installs Solar Flare Alert {version}. The saved Wi-Fi stays as it is. The external Wi-Fi manager is left as it is.",
      upgradeStep2: "Next, the browser asks which device to allow. Choose the lamp. It may be named USB Serial, CP2102, or USB JTAG.",
      upgradeChoose: "Choose the lamp and install",
      upgradeAgain: "Start again",
      upgradeProgress: "Copying the Solar Flare Alert program…",
      upgradeUpdated: "Solar Flare Alert {version} is on the lamp. The saved Wi-Fi is unchanged.",
      upgradeOld: "The lamp restarted with the previous setup program. Unplug it, plug it back in, and try again.",
      upgradeUnknown: "The copy finished and the lamp restarted. The computer did not see the new program announce itself. If the lamp joins Wi-Fi or opens WifiManager, the update is in place.",
    },
    de: {
      language: "English",
      browser: "Dieser Browser kann die Lampe nicht über USB erreichen. Öffnen Sie diese Seite in Firefox, Chrome oder Edge auf dem Computer. Safari kann das nicht.",
      cable: "Verbinden Sie die Lampe mit einem Daten-USB-Kabel mit diesem Computer.",
      working: "Die Lampe wird neu gestartet …",
      talking: "Die Lampe hört zu.",
      repl: "Die Lampe hat für den Computer nicht angehalten. Ziehen Sie das Kabel ab, stecken Sie es wieder ein und versuchen Sie es erneut.",
      raw: "Die Lampe hat keine Verbindung geöffnet, die der Computer nutzen kann. Ziehen Sie das Kabel ab, stecken Sie es wieder ein und versuchen Sie es erneut.",
      silent: "Die Lampe hat nichts gesendet.",
      exec: "Die Lampe hat den Befehl nicht angenommen. Ziehen Sie das Kabel ab, stecken Sie es wieder ein und versuchen Sie es erneut.",
      device: "Die Lampe hat einen Fehler gemeldet. Die Einzelheiten stehen unten.",
      size: "Die Übertragung ist vorzeitig abgebrochen. Die Lampe hat weiterhin ihr bisheriges Programm und ihr bisheriges WLAN.",
      cancel: "Es wurde keine Lampe ausgewählt.",
      missing: "Diese Seite konnte das Programm des Sonneneruptionsalarms nicht laden.",
      serialLog: "Meldungen der Lampe",
      homeTitle: "Sonneneruptionsalarm",
      homeWifi: "WLAN für den Sonneneruptionsalarm einrichten",
      homeWifiBody: "Speichert den Netzwerknamen und das Passwort auf der Lampe. Das Programm auf der Lampe bleibt, wie es ist.",
      homeUpgrade: "Versionen des Sonneneruptionsalarms",
      homeUpgradeBody: "Die Versionen des Sonneneruptionsalarms. Die Lampe kann geprüft werden, ob eine neuere Version vorliegt. Das gespeicherte WLAN bleibt, wie es ist.",
      wifiTitle: "WLAN für den Sonneneruptionsalarm einrichten",
      wifiLead: "Verbinden Sie die Lampe mit einem Daten-USB-Kabel mit diesem Computer. Diese Seite speichert das WLAN auf der Lampe. Sie ändert das Programm nicht.",
      wifiPrivate: "Das Passwort wird über das Kabel auf die Lampe geschrieben. Diese Seite sendet es nicht an einen Server.",
      ssid: "Netzwerkname",
      password: "Passwort",
      emptyPassword: "Leer lassen, wenn das Netzwerk kein Passwort hat.",
      show: "Passwort anzeigen",
      wifiButton: "Lampe verbinden und WLAN speichern",
      wifiReset: "Das WLAN ist bereits eingerichtet. Löschen.",
      wifiResetLead: "Damit wird das auf dem Sonneneruptionsalarm gespeicherte WLAN entfernt. Die Lampe vergisst dieses Netzwerk. Das Programm bleibt, wie es ist.",
      wifiResetChoose: "Lampe auswählen und WLAN löschen",
      wifiResetBack: "Stattdessen ein Netzwerk eingeben.",
      wifiResetting: "Das gespeicherte WLAN wird gelöscht …",
      wifiResetDone: "Das gespeicherte WLAN ist gelöscht. Sie können das Kabel abziehen. Das Licht blinkt, bis ein neues Netzwerk gespeichert ist.",
      wifiResetStill: "Die Lampe hat sich trotzdem mit einem WLAN verbunden. Ziehen Sie das Kabel ab, stecken Sie es wieder ein und versuchen Sie es erneut.",
      wifiResetUnknown: "Das gespeicherte Netzwerk wurde entfernt und die Lampe hat neu gestartet. Wenn das Licht blinkt, ist das WLAN gelöscht.",
      wifiResetFailed: "Das gespeicherte WLAN ist noch auf der Lampe. Ziehen Sie das Kabel ab, stecken Sie es wieder ein und versuchen Sie es erneut.",
      wifiNeedName: "Geben Sie den Netzwerknamen ein.",
      wifiSemicolon: "Netzwerkname und Passwort dürfen kein Semikolon enthalten.",
      wifiLong: "Der Netzwerkname darf höchstens 32 Zeichen haben.",
      wifiSaving: "Das WLAN wird auf der Lampe gespeichert …",
      stepCount: "Schritt {n} von {total}",
      wifiStep1: "Verbinden Sie den Sonneneruptionsalarm mit einem USB-Kabel, das Daten überträgt, mit diesem Computer. Warten Sie, bis das Licht blinkt.",
      wifiNextPlug: "Das Licht blinkt",
      wifiNotBlinking: "Das Licht blinkt nicht",
      wifiRunning: "Das Licht blinkt nicht, weil der Sonneneruptionsalarm bereits läuft. Er hat sich bereits mit einem WLAN verbunden. Sie können ihn so lassen oder ein anderes Netzwerk speichern.",
      wifiLeave: "So lassen",
      wifiReplace: "Ein anderes Netzwerk speichern",
      wifiSteady: "Sie können das Kabel abziehen. Die Lampe behält das WLAN, das sie bereits hat.",
      wifiStep2: "Geben Sie das WLAN ein, mit dem diese Lampe sich verbinden soll.",
      wifiNextNet: "Weiter",
      wifiStep3: "Als Nächstes fragt der Browser, welches Gerät erlaubt werden soll. Wählen Sie die Lampe. Sie kann USB Serial, CP2102 oder USB JTAG heissen.",
      wifiChoose: "Lampe auswählen",
      wifiAgain: "Von vorn beginnen",
      wifiConnected: "Die Lampe hat sich mit dem WLAN verbunden. Sie können das Kabel abziehen. Wenn das Licht aufhört zu blinken, ist sie verbunden.",
      wifiRejected: "Die Lampe hat sich nicht mit diesem Netzwerk verbunden. Prüfen Sie Name und Passwort und versuchen Sie es erneut.",
      wifiUnknown: "Das WLAN wurde auf die Lampe geschrieben, und die Lampe hat neu gestartet. Wenn das Licht aufhört zu blinken, ist sie verbunden.",
      upgradeTitle: "Versionen des Sonneneruptionsalarms",
      checkLamp: "Diese Lampe prüfen",
      checkStep1: "Verbinden Sie den Sonneneruptionsalarm mit einem USB-Kabel, das Daten überträgt, mit diesem Computer.",
      checkNextPlug: "Die Lampe ist angeschlossen",
      checkWorking: "Die Lampe wird geprüft. Bitte warten.",
      checkStep2: "Damit wird die Version von der Lampe gelesen. Das Programm und das WLAN bleiben, wie sie sind. Als Nächstes fragt der Browser, welches Gerät erlaubt werden soll. Wählen Sie die Lampe. Sie kann USB Serial, CP2102 oder USB JTAG heissen.",
      checkChoose: "Lampe auswählen und prüfen",
      checkCurrent: "Dieser Sonneneruptionsalarm hat Version {version}, die aktuelle Version auf dieser Seite.",
      checkOlder: "Dieser Sonneneruptionsalarm hat Version {version}. {latest} ist neuer.",
      checkUnrecorded: "Auf diesem Sonneneruptionsalarm ist keine Version gespeichert. Die aktuelle Version auf dieser Seite ist {latest}.",
      checkUnknown: "Dieser Sonneneruptionsalarm meldet {version}. Diese Version steht hier nicht. Die aktuelle Version auf dieser Seite ist {latest}.",
      checkNew: "Auf dieser Lampe ist das Programm des Sonneneruptionsalarms noch nicht vorhanden. Die aktuelle Version auf dieser Seite ist {latest}.",
      latest: "Aktuell",
      allVersions: "Alle Versionen",
      install: "Installieren",
      upgradeBack: "Alle Versionen",
      upgradeStep1: "Verbinden Sie den Sonneneruptionsalarm mit einem USB-Kabel, das Daten überträgt, mit diesem Computer. Warten Sie, bis das Licht blinkt.",
      upgradeNextPlug: "Das Licht blinkt",
      upgradeInstalling: "Damit wird Sonneneruptionsalarm {version} installiert. Das gespeicherte WLAN bleibt, wie es ist. Der externe WLAN-Manager bleibt, wie er ist.",
      upgradeStep2: "Als Nächstes fragt der Browser, welches Gerät erlaubt werden soll. Wählen Sie die Lampe. Sie kann USB Serial, CP2102 oder USB JTAG heissen.",
      upgradeChoose: "Lampe auswählen und installieren",
      upgradeAgain: "Von vorn beginnen",
      upgradeProgress: "Das Programm des Sonneneruptionsalarms wird kopiert …",
      upgradeUpdated: "Sonneneruptionsalarm {version} ist auf der Lampe. Das gespeicherte WLAN ist unverändert.",
      upgradeOld: "Die Lampe ist mit dem bisherigen Einrichtungsprogramm neu gestartet. Ziehen Sie das Kabel ab, stecken Sie es wieder ein und versuchen Sie es erneut.",
      upgradeUnknown: "Die Kopie ist fertig und die Lampe hat neu gestartet. Der Computer hat das neue Programm nicht erkannt. Wenn die Lampe ins WLAN geht oder WifiManager öffnet, ist die Aktualisierung da.",
    },
  };

  function language() {
    var stored = localStorage.getItem("lamp-lang");
    if (stored === "de" || stored === "en") return stored;
    return navigator.language && navigator.language.toLowerCase().indexOf("de") === 0 ? "de" : "en";
  }

  function text() {
    return copy[language()];
  }

  function fill(root) {
    var strings = text();
    document.documentElement.lang = language() === "de" ? "de" : "en";
    root.querySelectorAll("[data-i18n]").forEach(function (node) {
      var key = node.getAttribute("data-i18n");
      if (strings[key]) node.textContent = strings[key];
    });
    var switcher = root.querySelector("[data-lang]");
    if (switcher) switcher.textContent = strings.language;
  }

  function bindLanguage(root, redraw) {
    var switcher = root.querySelector("[data-lang]");
    if (!switcher) return;
    switcher.addEventListener("click", function () {
      localStorage.setItem("lamp-lang", language() === "de" ? "en" : "de");
      fill(root);
      if (redraw) redraw();
    });
  }

  function setStatus(node, kind, message) {
    node.hidden = false;
    node.dataset.kind = kind || "";
    node.textContent = message;
  }

  function friendly(error) {
    var strings = text();
    if (!error) return strings.exec;
    if (error.name === "NotFoundError" || error.name === "AbortError") return strings.cancel;
    if (error.message === "missing-file") return strings.missing;
    if (strings[error.message]) return strings[error.message];
    return strings.exec;
  }

  function failureText(error) {
    var parts = [];
    if (error && error.captured) parts.push(String(error.captured));
    if (error && error.detail) parts.push(String(error.detail));
    if (!parts.length) parts.push(text().silent);
    if (error && error.message && !text()[error.message]) {
      parts.push((error.name || "Error") + ": " + error.message);
    }
    return parts.join("\n");
  }

  function rememberLog(pre, text) {
    if (pre) pre.textContent = text || "";
  }

  async function withLamp(work, options) {
    if (!navigator.serial) {
      var missing = new Error("browser");
      throw missing;
    }
    var port = await navigator.serial.requestPort();
    var lamp = new LampPort(port);
    lamp.onText = options && options.onText;
    try {
      await lamp.open();
      await lamp.prepare(options || {});
      return await work(lamp);
    } finally {
      await lamp.close();
    }
  }

  function initHome(root) {
    fill(root);
    bindLanguage(root);
  }

  function showStep(root, n, total) {
    root.querySelectorAll("[data-step]").forEach(function (section) {
      section.hidden = section.getAttribute("data-step") !== String(n);
    });
    var count = root.querySelector("[data-step-count]");
    if (!count) return;
    if (n > total) {
      count.hidden = true;
      return;
    }
    count.hidden = false;
    count.textContent = text().stepCount.replace("{n}", n).replace("{total}", total);
  }

  function initWifi(root) {
    var form = root.querySelector("form");
    var status = root.querySelector(".status");
    var log = root.querySelector("pre");
    var choose = root.querySelector("#choose");
    var clear = root.querySelector("#clear");
    var reset = root.querySelector("#reset");
    var resetBack = root.querySelector("#reset-back");
    var again = root.querySelector("#again");
    var warning = root.querySelector(".warning");
    var step = 1;
    var clearing = false;

    function showClearStep() {
      step = "clear";
      root.querySelectorAll("[data-step]").forEach(function (section) {
        section.hidden = section.getAttribute("data-step") !== "clear";
      });
      var count = root.querySelector("[data-step-count]");
      if (!count) return;
      count.hidden = false;
      count.textContent = text().stepCount.replace("{n}", "2").replace("{total}", "2");
    }

    function showNamed(name) {
      root.querySelectorAll("[data-step]").forEach(function (section) {
        section.hidden = section.getAttribute("data-step") !== name;
      });
      var count = root.querySelector("[data-step-count]");
      if (count) count.hidden = true;
    }

    function redraw() {
      fill(root);
      if (step === "clear") showClearStep();
      else if (step === "running" || step === "steady") showNamed(step);
      else showStep(root, step, 3);
      if (!navigator.serial) setStatus(warning, "bad", text().browser);
    }

    redraw();
    bindLanguage(root, redraw);
    if (navigator.serial) warning.hidden = true;

    root.querySelector("[data-goto='2']").addEventListener("click", function () {
      step = 2;
      showStep(root, step, 3);
    });

    root.querySelector("#not-blinking").addEventListener("click", function () {
      status.hidden = true;
      step = "running";
      showNamed(step);
    });

    root.querySelector("#replace").addEventListener("click", function () {
      status.hidden = true;
      step = 2;
      showStep(root, step, 3);
    });

    root.querySelector("#leave").addEventListener("click", function () {
      status.hidden = true;
      step = "steady";
      showNamed(step);
    });

    form.addEventListener("submit", function (event) {
      event.preventDefault();
      var strings = text();
      var ssid = form.ssid.value.trim();
      var password = form.password.value;
      status.hidden = true;
      if (!ssid) {
        setStatus(status, "bad", strings.wifiNeedName);
        return;
      }
      if (ssid.length > 32) {
        setStatus(status, "bad", strings.wifiLong);
        return;
      }
      if (ssid.indexOf(";") !== -1 || password.indexOf(";") !== -1 || password.indexOf("\n") !== -1) {
        setStatus(status, "bad", strings.wifiSemicolon);
        return;
      }
      step = 3;
      clearing = false;
      showStep(root, step, 3);
    });

    reset.addEventListener("click", function () {
      status.hidden = true;
      clearing = true;
      showClearStep();
    });

    resetBack.addEventListener("click", function () {
      status.hidden = true;
      clearing = false;
      step = 2;
      showStep(root, step, 3);
    });

    choose.addEventListener("click", async function () {
      var strings = text();
      if (!navigator.serial) {
        setStatus(warning, "bad", strings.browser);
        return;
      }
      choose.disabled = true;
      step = 4;
      showStep(root, step, 3);
      again.hidden = true;
      setStatus(status, "", strings.working);
      try {
        var watched = await withLamp(async function (lamp) {
          setStatus(status, "", strings.wifiSaving);
          await saveWifi(lamp, form.ssid.value.trim(), form.password.value);
          return lamp.watch(wifiResult);
        });
        rememberLog(log, watched.text);
        if (watched.result === "connected") setStatus(status, "ok", strings.wifiConnected);
        else if (watched.result === "rejected") setStatus(status, "bad", strings.wifiRejected);
        else if (watched.result === "error") setStatus(status, "bad", strings.device);
        else setStatus(status, "", strings.wifiUnknown);
        if (watched.result !== "connected") again.hidden = false;
      } catch (error) {
        rememberLog(log, failureText(error));
        setStatus(status, "bad", error.message === "browser" ? strings.browser : friendly(error));
        again.hidden = false;
      } finally {
        choose.disabled = false;
      }
    });

    clear.addEventListener("click", async function () {
      var strings = text();
      if (!navigator.serial) {
        setStatus(warning, "bad", strings.browser);
        return;
      }
      clear.disabled = true;
      step = 4;
      showStep(root, step, 3);
      again.hidden = true;
      setStatus(status, "", strings.working);
      try {
        var watched = await withLamp(async function (lamp) {
          setStatus(status, "", strings.wifiResetting);
          await clearWifi(lamp);
          return lamp.watch(resetResult);
        });
        rememberLog(log, watched.text);
        if (watched.result === "cleared") setStatus(status, "ok", strings.wifiResetDone);
        else if (watched.result === "still") setStatus(status, "bad", strings.wifiResetStill);
        else if (watched.result === "error") setStatus(status, "bad", strings.device);
        else setStatus(status, "", strings.wifiResetUnknown);
        if (watched.result !== "cleared") again.hidden = false;
      } catch (error) {
        rememberLog(log, failureText(error));
        setStatus(status, "bad", error.message === "browser" ? strings.browser : friendly(error));
        again.hidden = false;
      } finally {
        clear.disabled = false;
      }
    });

    again.addEventListener("click", function () {
      status.hidden = true;
      again.hidden = true;
      if (clearing) showClearStep();
      else {
        step = 2;
        showStep(root, step, 3);
      }
    });

    var reveal = root.querySelector(".show-password input");
    reveal.addEventListener("change", function () {
      form.password.type = reveal.checked ? "text" : "password";
    });
  }

  function formatReleaseDate(iso) {
    var parts = iso.split("-");
    var locale = language() === "de" ? "de-CH" : "en-GB";
    if (parts.length === 2) {
      var month = new Date(Date.UTC(Number(parts[0]), Number(parts[1]) - 1, 1));
      return month.toLocaleDateString(locale, { month: "long", year: "numeric", timeZone: "UTC" });
    }
    var date = new Date(Date.UTC(Number(parts[0]), Number(parts[1]) - 1, Number(parts[2])));
    return date.toLocaleDateString(locale, {
      day: "numeric",
      month: "long",
      year: "numeric",
      timeZone: "UTC",
    });
  }

  function initUpgrade(root) {
    var releases = root.querySelector("#releases");
    var wizard = root.querySelector("#wizard");
    var status = root.querySelector(".status");
    var log = root.querySelector("pre");
    var choose = root.querySelector("#choose");
    var again = root.querySelector("#again");
    var back = root.querySelector("#back");
    var check = root.querySelector("#check");
    var installLatest = root.querySelector("#install-latest");
    var warning = root.querySelector(".warning");
    var versions = [];
    var chosen = null;
    var mode = "install";
    var step = 1;

    function redraw() {
      fill(root);
      if (!chosen) {
        releases.hidden = false;
        wizard.hidden = true;
        if (check) check.hidden = false;
        if (installLatest) installLatest.hidden = true;
        renderReleases();
      } else {
        releases.hidden = true;
        wizard.hidden = false;
        if (check) check.hidden = true;
        showStep(root, step, 2);
        var installing = root.querySelector("[data-installing]");
        var deviceStep = root.querySelector("[data-device-step]");
        if (mode === "check") {
          var plugLead = root.querySelector("[data-step='1'] .lead");
          var plugNext = root.querySelector("[data-step='1'] [data-goto='2']");
          if (plugLead) plugLead.textContent = text().checkStep1;
          if (plugNext) plugNext.textContent = text().checkNextPlug;
          if (installing) installing.textContent = text().checkStep2;
          if (deviceStep) deviceStep.hidden = true;
          choose.textContent = text().checkChoose;
        } else {
          if (installing) {
            installing.textContent = text().upgradeInstalling.replace("{version}", chosen.version);
          }
          if (deviceStep) deviceStep.hidden = step !== 2;
          choose.textContent = text().upgradeChoose;
        }
        if (installLatest && !installLatest.hidden) {
          var newest = versions.filter(function (item) {
            return item.latest;
          })[0];
          installLatest.textContent = text().install + (newest ? " " + newest.version : "");
        }
      }
      if (!navigator.serial) setStatus(warning, "bad", text().browser);
    }

    function releaseCard(item, featured) {
      var strings = text();
      var card = document.createElement("article");
      card.className = featured ? "release featured" : "release";
      var title = document.createElement("h2");
      title.textContent = item.version;
      if (item.latest) {
        var badge = document.createElement("span");
        badge.className = "badge";
        badge.textContent = strings.latest;
        title.appendChild(document.createTextNode(" "));
        title.appendChild(badge);
      }
      var date = document.createElement("p");
      date.className = "release-date";
      date.textContent = formatReleaseDate(item.date);
      var notes = document.createElement("p");
      notes.textContent = (item.notes && (item.notes[language()] || item.notes.en)) || "";
      var actions = document.createElement("p");
      actions.className = "release-actions";
      var install = document.createElement("button");
      install.type = "button";
      install.className = "action";
      install.textContent = strings.install + " " + item.version;
      install.addEventListener("click", function () {
        mode = "install";
        chosen = item;
        step = 1;
        status.hidden = true;
        again.hidden = true;
        if (installLatest) installLatest.hidden = true;
        redraw();
      });
      actions.appendChild(install);
      card.appendChild(title);
      card.appendChild(date);
      card.appendChild(notes);
      card.appendChild(actions);
      return card;
    }

    function renderReleases() {
      var strings = text();
      releases.replaceChildren();
      var latest = versions.filter(function (item) {
        return item.latest;
      })[0];
      if (latest) releases.appendChild(releaseCard(latest, true));
      var heading = document.createElement("h2");
      heading.textContent = strings.allVersions;
      releases.appendChild(heading);
      versions.forEach(function (item) {
        releases.appendChild(releaseCard(item, false));
      });
    }

    fill(root);
    bindLanguage(root, redraw);
    if (navigator.serial) warning.hidden = true;
    else setStatus(warning, "bad", text().browser);

    root.querySelector("[data-goto='2']").addEventListener("click", function () {
      step = 2;
      showStep(root, step, 2);
    });

    choose.addEventListener("click", async function () {
      var strings = text();
      if (!chosen) return;
      if (!navigator.serial) {
        setStatus(warning, "bad", strings.browser);
        return;
      }
      choose.disabled = true;
      step = 3;
      showStep(root, step, 2);
      again.hidden = true;
      if (installLatest) installLatest.hidden = true;
      setStatus(status, "", mode === "check" ? strings.checkWorking : strings.working);
      var details = log ? log.closest("details") : null;
      if (details) details.open = true;
      try {
        if (mode === "check") {
          var state = await withLamp(
            async function (lamp) {
              var found = await readLampState(lamp);
              try {
                await lamp.hardReset(false);
              } catch (error) {
                /* The version was already read. */
              }
              return found;
            },
            {
              reset: false,
              onText: function (received) {
                rememberLog(log, received);
              },
            }
          );
          rememberLog(log, "");
          if (details) details.open = false;
          var verdict = judgeVersion(state, versions);
          var latestName = verdict.latest ? verdict.latest.version : "";
          var shown = verdict.version || "";
          function offerLatest() {
            if (!installLatest || !verdict.latest) return;
            if (verdict.status === "current") return;
            installLatest.hidden = false;
            installLatest.textContent = strings.install + " " + latestName;
          }
          if (verdict.status === "current") {
            setStatus(status, "ok", strings.checkCurrent.replace("{version}", shown));
          } else if (verdict.status === "new") {
            setStatus(status, "", strings.checkNew.replace("{latest}", latestName));
            offerLatest();
          } else if (verdict.status === "older") {
            setStatus(
              status,
              "",
              strings.checkOlder.replace("{version}", shown).replace("{latest}", latestName)
            );
            offerLatest();
          } else {
            setStatus(
              status,
              "",
              strings.checkUnknown.replace("{version}", shown).replace("{latest}", latestName)
            );
          }
        } else {
          var files = [];
          for (var i = 0; i < chosen.files.length; i++) {
            files.push({
              name: chosen.files[i].name,
              bytes: await loadProgram(chosen.files[i].file),
            });
          }
          var totalBytes = 0;
          files.forEach(function (file) {
            totalBytes += file.bytes.length;
          });
          var watched = await withLamp(async function (lamp) {
            var copied = 0;
            for (var n = 0; n < files.length; n++) {
              await writeProgramFile(lamp, files[n].name, files[n].bytes, function (done) {
                setStatus(status, "", strings.upgradeProgress + " " + (copied + done) + " / " + totalBytes);
              });
              copied += files[n].bytes.length;
            }
            return lamp.watch(programResult(chosen.version));
          });
          rememberLog(log, watched.text);
          if (watched.result === "updated") {
            setStatus(status, "ok", strings.upgradeUpdated.replace("{version}", chosen.version));
          } else if (watched.result === "error") setStatus(status, "bad", strings.device);
          else setStatus(status, "", strings.upgradeUnknown);
          if (watched.result !== "updated") again.hidden = false;
        }
      } catch (error) {
        rememberLog(log, failureText(error));
        setStatus(status, "bad", error.message === "browser" ? strings.browser : friendly(error));
        again.hidden = false;
      } finally {
        choose.disabled = false;
      }
    });

    again.addEventListener("click", function () {
      status.hidden = true;
      again.hidden = true;
      step = 1;
      showStep(root, step, 2);
    });

    back.addEventListener("click", function () {
      chosen = null;
      mode = "install";
      step = 1;
      status.hidden = true;
      again.hidden = true;
      if (installLatest) installLatest.hidden = true;
      redraw();
    });

    if (check) {
      check.addEventListener("click", function () {
        var latest = versions.filter(function (item) {
          return item.latest;
        })[0];
        if (!latest) return;
        mode = "check";
        chosen = latest;
        step = 1;
        status.hidden = true;
        again.hidden = true;
        if (installLatest) installLatest.hidden = true;
        redraw();
      });
    }

    if (installLatest) {
      installLatest.addEventListener("click", function () {
        var latest = versions.filter(function (item) {
          return item.latest;
        })[0];
        if (!latest) return;
        mode = "install";
        chosen = latest;
        step = 2;
        status.hidden = true;
        again.hidden = true;
        installLatest.hidden = true;
        redraw();
      });
    }

    fetch("versions.json", { cache: "no-store" })
      .then(function (response) {
        if (!response.ok) throw new Error("missing-file");
        return response.json();
      })
      .then(function (loaded) {
        versions = loaded;
        redraw();
      })
      .catch(function () {
        fill(root);
        setStatus(warning, "bad", text().missing);
      });
  }

  async function loadProgram(url) {
    var urls = url ? [url] : ["wifi_manager.py", "../micropython/wifi_manager.py"];
    for (var i = 0; i < urls.length; i++) {
      try {
        var response = await fetch(urls[i]);
        if (!response.ok) continue;
        return new Uint8Array(await response.arrayBuffer());
      } catch (error) {
        /* Try the next location. */
      }
    }
    throw new Error("missing-file");
  }

  window.LampTools = {
    initHome: initHome,
    initWifi: initWifi,
    initUpgrade: initUpgrade,
    wifiResult: wifiResult,
    programResult: programResult,
    judgeVersion: judgeVersion,
    bytesToBase64: bytesToBase64,
  };
})();
