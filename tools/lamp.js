(function () {
  var copy = {
    en: {
      language: "Deutsch",
      homeTitle: "Solar Flare Alert",
      homeWifi: "Set up Wi-Fi for the Solar Flare Alert",
      homeWifiBody: "A program on this computer saves the network on the lamp. The program on the lamp stays as it is.",
      homeUpgrade: "Solar Flare Alert versions",
      homeUpgradeBody: "Versions of the Solar Flare Alert. A program on this computer reads the lamp. The saved Wi-Fi stays as it is.",
      wifiTitle: "Set up Wi-Fi for the Solar Flare Alert",
      wifiLead: "The browser cannot write to this lamp. A program on the computer can.",
      wifiPlug: "Plug the Solar Flare Alert into this computer with a USB cable that carries data.",
      wifiRunning: "When the light is not blinking, the Solar Flare Alert is already running and has already joined a Wi-Fi network. You can leave it as it is, or save a different network with the program below.",
      download: "Download the setup program",
      wifiRun: "Open Terminal. Go to the folder where this file was saved. On a Mac that is usually Downloads. The program asks for the network name and the password.",
      cmdWifi: "cd ~/Downloads\npython3 lamp_setup.py wifi",
      wifiPrivate: "The password is typed into that program and written to the lamp over the cable. It is not sent to a server. Leave it empty when the network has no password.",
      wifiClearLead: "To remove the saved Wi-Fi, run this instead. The program on the lamp stays as it is. Afterwards the light blinks until a new network is saved.",
      cmdClear: "cd ~/Downloads\npython3 lamp_setup.py clear",
      upgradeTitle: "Solar Flare Alert versions",
      programLead: "The browser cannot check this lamp. A program on the computer can.",
      programPlug: "Plug the Solar Flare Alert into this computer with a USB cable that carries data.",
      programCheck: "Open Terminal. Go to the folder where this file was saved. On a Mac that is usually Downloads. This reads the version. It does not change the program or the Wi-Fi.",
      cmdCheck: "cd ~/Downloads\npython3 lamp_setup.py check",
      programInstall: "To put the current version on the lamp, run this instead. The saved Wi-Fi stays as it is. The external Wi-Fi manager stays as it is.",
      cmdInstall: "cd ~/Downloads\npython3 lamp_setup.py install",
      latest: "Latest",
      allVersions: "All versions",
      missing: "This page could not load the list of versions.",
    },
    de: {
      language: "English",
      homeTitle: "Sonneneruptionsalarm",
      homeWifi: "WLAN für den Sonneneruptionsalarm einrichten",
      homeWifiBody: "Ein Programm auf diesem Computer speichert das Netzwerk auf der Lampe. Das Programm auf der Lampe bleibt, wie es ist.",
      homeUpgrade: "Versionen des Sonneneruptionsalarms",
      homeUpgradeBody: "Die Versionen des Sonneneruptionsalarms. Ein Programm auf diesem Computer liest die Lampe. Das gespeicherte WLAN bleibt, wie es ist.",
      wifiTitle: "WLAN für den Sonneneruptionsalarm einrichten",
      wifiLead: "Der Browser kann nicht auf diese Lampe schreiben. Ein Programm auf dem Computer kann das.",
      wifiPlug: "Verbinden Sie den Sonneneruptionsalarm mit einem USB-Kabel, das Daten überträgt, mit diesem Computer.",
      wifiRunning: "Wenn das Licht nicht blinkt, läuft der Sonneneruptionsalarm bereits und hat sich bereits mit einem WLAN verbunden. Sie können ihn so lassen oder mit dem Programm unten ein anderes Netzwerk speichern.",
      download: "Einrichtungsprogramm herunterladen",
      wifiRun: "Öffnen Sie das Terminal. Wechseln Sie in den Ordner, in dem diese Datei gespeichert wurde. Auf einem Mac ist das meist Downloads. Das Programm fragt nach dem Netzwerknamen und dem Passwort.",
      cmdWifi: "cd ~/Downloads\npython3 lamp_setup.py de wifi",
      wifiPrivate: "Das Passwort wird in dieses Programm eingegeben und über das Kabel auf die Lampe geschrieben. Es wird nicht an einen Server gesendet. Leer lassen, wenn das Netzwerk kein Passwort hat.",
      wifiClearLead: "Um das gespeicherte WLAN zu entfernen, führen Sie stattdessen dies aus. Das Programm auf der Lampe bleibt, wie es ist. Danach blinkt das Licht, bis ein neues Netzwerk gespeichert ist.",
      cmdClear: "cd ~/Downloads\npython3 lamp_setup.py de clear",
      upgradeTitle: "Versionen des Sonneneruptionsalarms",
      programLead: "Der Browser kann diese Lampe nicht prüfen. Ein Programm auf dem Computer kann das.",
      programPlug: "Verbinden Sie den Sonneneruptionsalarm mit einem USB-Kabel, das Daten überträgt, mit diesem Computer.",
      programCheck: "Öffnen Sie das Terminal. Wechseln Sie in den Ordner, in dem diese Datei gespeichert wurde. Auf einem Mac ist das meist Downloads. Damit wird die Version gelesen. Das Programm und das WLAN bleiben, wie sie sind.",
      cmdCheck: "cd ~/Downloads\npython3 lamp_setup.py de check",
      programInstall: "Um die aktuelle Version auf die Lampe zu setzen, führen Sie stattdessen dies aus. Das gespeicherte WLAN bleibt, wie es ist. Der externe WLAN-Manager bleibt, wie er ist.",
      cmdInstall: "cd ~/Downloads\npython3 lamp_setup.py de install",
      latest: "Aktuell",
      allVersions: "Alle Versionen",
      missing: "Diese Seite konnte die Versionsliste nicht laden.",
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
    document.title = strings.homeTitle;
    var title = root.querySelector("h1");
    if (title && title.getAttribute("data-i18n") && strings[title.getAttribute("data-i18n")]) {
      document.title = strings[title.getAttribute("data-i18n")];
    }
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

  function initHome(root) {
    fill(root);
    bindLanguage(root);
  }

  function initWifi(root) {
    fill(root);
    bindLanguage(root);
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
    var warning = root.querySelector(".warning");
    var versions = [];

    function releaseCard(item, featured) {
      var strings = text();
      var card = document.createElement("article");
      card.className = featured ? "release featured" : "release";
      var title = document.createElement("h2");
      title.textContent = item.version;
      if (item.latest) {
        var badge = document.createElement("span");
        badge.className = "badge";
        badge.textContent = " " + strings.latest;
        title.appendChild(badge);
      }
      var date = document.createElement("p");
      date.className = "release-date";
      date.textContent = formatReleaseDate(item.date);
      var notes = document.createElement("p");
      notes.textContent = (item.notes && (item.notes[language()] || item.notes.en)) || "";
      card.appendChild(title);
      card.appendChild(date);
      card.appendChild(notes);
      return card;
    }

    function render() {
      if (!releases) return;
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

    function redraw() {
      fill(root);
      render();
    }

    fill(root);
    bindLanguage(root, redraw);
    fetch("versions.json", { cache: "no-store" })
      .then(function (response) {
        if (!response.ok) throw new Error("missing");
        return response.json();
      })
      .then(function (loaded) {
        versions = loaded;
        render();
      })
      .catch(function () {
        if (!warning) return;
        warning.hidden = false;
        warning.textContent = text().missing;
      });
  }

  window.LampTools = {
    initHome: initHome,
    initWifi: initWifi,
    initUpgrade: initUpgrade,
  };
})();
