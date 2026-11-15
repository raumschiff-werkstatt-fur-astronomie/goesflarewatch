(function () {
  var copy = {
    en: {
      language: "Deutsch",
      homeTitle: "Solar Flare Alert",
      homeWifi: "Set up Wi-Fi for the Solar Flare Alert",
      homeWifiBody: "When the light is blinking, join the Wi-Fi network Solar Flare Alert on a phone and choose your network on the page.",
      homeUpgrade: "Solar Flare Alert versions",
      navHome: "Solar Flare Alert",
      navWifi: "Set up Wi-Fi",
      navVersions: "Versions",
      homeUpgradeBody: "These are the published versions of the Solar Flare Alert. A program on this computer reads the version from the lamp. The saved Wi-Fi will not be affected.",
      wifiTitle: "Set up Wi-Fi for the Solar Flare Alert",
      wifiLead: "When the light is blinking, the lamp is not connected to the Wi-Fi. On a phone, join the Wi-Fi network named Solar Flare Alert. It has no password. It is only the lamp.",
      wifiPhone: "The phone should open a setup page. Choose a network and enter its password. The password stays on the lamp. A network that asks for a username while connecting cannot be used. If that is your only network, turn on the phone's personal hotspot, give it a name and a password, and choose that name on the page. The lamp then uses the phone's mobile data.",
      wifiAddress: "If the phone does not open the page, open the browser and go to http://192.168.4.1. After the lamp joins, it restarts. The light blinks once more, then it stays on. You can leave Solar Flare Alert and return to your own Wi-Fi.",
      wifiChange: "To choose a different network later, switch that network off and turn the lamp off and on. The light blinks, and Solar Flare Alert appears again.",
      wifiComputer: "With a computer, you can set up the lamp from a terminal.",
      wifiVersion: "The phone setup is part of the current software version. Put that version on the lamp from the Versions page. Until then, the lamp does not open a network named Solar Flare Alert.",
      wifiPlug: "Plug the Solar Flare Alert into this computer with a USB cable that carries data.",
      wifiRunning: "If the light is not blinking, the lamp has already joined a Wi-Fi network. You can leave that network as it is.",
      download: "Download the setup program",
      wifiRun: "Open Terminal and go to the folder where you saved the file. On a Mac or a PC, that folder is usually Downloads. The program lists the networks the lamp can see. Choose one, and then enter the username and the password.",
      cmdWifi: "cd ~/Downloads\npython3 lamp_setup.py wifi",
      wifiPrivate: "The password is written to the lamp over the cable and is not sent to a server. Leave the username empty if the network does not use one. Leave the password empty if the network does not use one.",
      wifiClearLead: "To remove the saved Wi-Fi network, run the command below. The program on the lamp stays as it is. The light blinks until a new network is saved.",
      cmdClear: "cd ~/Downloads\npython3 lamp_setup.py clear",
      upgradeTitle: "Solar Flare Alert versions",
      programLead: "The browser cannot check this lamp. Use the program below on this computer.",
      programPlug: "Plug the Solar Flare Alert into this computer with a USB cable that carries data.",
      programCheck: "Open Terminal and go to the folder where you saved the file. On a Mac or a PC, that folder is usually Downloads. This check reads the version from the lamp and reports whether the lamp is connected to the Wi-Fi. It does not change the program or the Wi-Fi setup.",
      cmdCheck: "cd ~/Downloads\npython3 lamp_setup.py check",
      programInstall: "To put the current software version on the lamp, run the command below. The saved Wi-Fi will not be affected.",
      cmdInstall: "cd ~/Downloads\npython3 lamp_setup.py install",
      latest: "Latest",
      allVersions: "All versions",
      missing: "This page could not load the list of versions.",
    },
    de: {
      language: "English",
      homeTitle: "Sonneneruptionsalarm",
      homeWifi: "WLAN für den Sonneneruptionsalarm einrichten",
      homeWifiBody: "Wenn das Licht blinkt, verbinden Sie das Telefon mit dem WLAN Solar Flare Alert und wählen Sie auf der Seite Ihr Netzwerk.",
      homeUpgrade: "Versionen des Sonneneruptionsalarms",
      navHome: "Sonneneruptionsalarm",
      navWifi: "WLAN einrichten",
      navVersions: "Versionen",
      homeUpgradeBody: "Die Versionen des Sonneneruptionsalarms. Ein Programm auf diesem Computer liest die Lampe. Das gespeicherte WLAN wird nicht verändert.",
      wifiTitle: "WLAN für den Sonneneruptionsalarm einrichten",
      wifiLead: "Wenn das Licht blinkt, ist die Lampe nicht mit dem WLAN verbunden. Verbinden Sie das Telefon mit dem WLAN Solar Flare Alert. Es hat kein Passwort. Es ist nur die Lampe.",
      wifiPhone: "Das Telefon sollte eine Einrichtungsseite öffnen. Wählen Sie ein Netzwerk und geben Sie sein Passwort ein. Das Passwort bleibt auf der Lampe. Ein Netzwerk, das beim Verbinden einen Benutzernamen verlangt, kann die Lampe nicht benutzen. Wenn Sie nur ein solches Netzwerk haben, schalten Sie den persönlichen Hotspot des Telefons ein, geben Sie ihm einen Namen und ein Passwort, und wählen Sie diesen Namen auf der Seite. Die Lampe benutzt dann die mobilen Daten des Telefons.",
      wifiAddress: "Wenn das Telefon die Seite nicht öffnet, öffnen Sie den Browser und gehen Sie zu http://192.168.4.1. Nach dem Beitritt startet die Lampe neu. Das Licht blinkt noch einmal, danach leuchtet es dauerhaft. Sie können Solar Flare Alert verlassen und zu Ihrem eigenen WLAN zurückkehren.",
      wifiChange: "Um später ein anderes Netzwerk zu wählen, schalten Sie dieses Netzwerk aus und die Lampe aus und wieder ein. Das Licht blinkt, und Solar Flare Alert erscheint wieder.",
      wifiComputer: "Mit einem Computer können Sie die Lampe vom Terminal aus einrichten.",
      wifiVersion: "Die Einrichtung mit dem Telefon gehört zur aktuellen Softwareversion. Setzen Sie diese Version über die Seite Versionen auf die Lampe. Vorher öffnet die Lampe kein Netzwerk mit dem Namen Solar Flare Alert.",
      wifiPlug: "Verbinden Sie den Sonneneruptionsalarm mit einem USB-Kabel, das Daten überträgt, mit diesem Computer.",
      wifiRunning: "Wenn das Licht nicht blinkt, hat die Lampe bereits ein WLAN. Sie können dieses Netzwerk so lassen.",
      download: "Einrichtungsprogramm herunterladen",
      wifiRun: "Öffnen Sie das Terminal und wechseln Sie in den Ordner, in dem Sie die Datei gespeichert haben. Auf einem Mac oder einem PC ist das meistens der Ordner Downloads. Das Programm zeigt die Netzwerke, die die Lampe sieht. Wählen Sie eines aus und geben Sie danach den Benutzernamen und das Passwort ein.",
      cmdWifi: "cd ~/Downloads\npython3 lamp_setup.py de wifi",
      wifiPrivate: "Das Passwort wird über das Kabel auf die Lampe geschrieben und nicht an einen Server gesendet. Lassen Sie den Benutzernamen leer, wenn das Netzwerk keinen benutzt. Lassen Sie das Passwort leer, wenn das Netzwerk keines hat.",
      wifiClearLead: "Um das gespeicherte WLAN zu entfernen, führen Sie den Befehl unten aus. Das Programm auf der Lampe bleibt, wie es ist. Danach blinkt das Licht, bis ein neues Netzwerk gespeichert ist.",
      cmdClear: "cd ~/Downloads\npython3 lamp_setup.py de clear",
      upgradeTitle: "Versionen des Sonneneruptionsalarms",
      programLead: "Der Browser kann diese Lampe nicht prüfen. Benutzen Sie dafür das Programm unten auf diesem Computer.",
      programPlug: "Verbinden Sie den Sonneneruptionsalarm mit einem USB-Kabel, das Daten überträgt, mit diesem Computer.",
      programCheck: "Öffnen Sie das Terminal und wechseln Sie in den Ordner, in dem Sie die Datei gespeichert haben. Auf einem Mac oder einem PC ist das meistens der Ordner Downloads. Diese Prüfung liest die Version von der Lampe und meldet, ob die Lampe mit dem WLAN verbunden ist. Sie ändert das Programm und die WLAN-Einrichtung nicht.",
      cmdCheck: "cd ~/Downloads\npython3 lamp_setup.py de check",
      programInstall: "Um die aktuelle Softwareversion auf die Lampe zu setzen, führen Sie den Befehl unten aus. Das gespeicherte WLAN wird nicht verändert.",
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
