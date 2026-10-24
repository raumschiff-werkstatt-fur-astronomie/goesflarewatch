#!/usr/bin/env python3
"""Copy the public lamp site and reject a catalog that cannot be installed."""

import json
import shutil
import sys
from pathlib import Path

PUBLIC_FILES = (
    "index.html",
    "set-up-wifi.html",
    "update-software.html",
    "lamp.css",
    "lamp.js",
    "lamp_setup.py",
    "versions.json",
)


def fail(message):
    raise SystemExit(message)


def main():
    if len(sys.argv) != 3:
        fail("usage: pack_lamp_site.py SOURCE DEST")
    source = Path(sys.argv[1]).resolve()
    dest = Path(sys.argv[2]).resolve()
    if not source.is_dir():
        fail(f"missing source {source}")
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)

    for name in PUBLIC_FILES:
        src = source / name
        if not src.is_file():
            fail(f"missing {name}")
        shutil.copy2(src, dest / name)

    versions = source / "versions"
    if not versions.is_dir():
        fail("missing versions/")
    copied = []
    for path in sorted(versions.rglob("*")):
        if not path.is_file():
            continue
        if path.suffix != ".py" or path.name == "wifi_manager.py":
            fail(f"refusing {path.relative_to(source)}")
        relative = path.relative_to(source)
        target = dest / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
        copied.append(relative.as_posix())

    if list(dest.rglob("wifi_manager.py")):
        fail("wifi_manager.py was packed")

    catalog = json.loads((dest / "versions.json").read_text(encoding="utf-8"))
    if not isinstance(catalog, list) or not catalog:
        fail("versions.json must be a non-empty list")
    latest = [item for item in catalog if item.get("latest") is True]
    if len(latest) != 1:
        fail(f"expected exactly one latest release, found {len(latest)}")

    listed = []
    for item in catalog:
        version = item.get("version")
        files = item.get("files")
        if not version or not isinstance(files, list) or not files:
            fail(f"{version or 'release'} has no files")
        for entry in files:
            name = entry.get("name")
            relative = entry.get("file")
            if not name or not relative or Path(name).name == "wifi_manager.py":
                fail(f"refusing file entry {entry!r}")
            if Path(relative).name != name or name != Path(name).name:
                fail(f"{name} does not match {relative}")
            target = (dest / relative).resolve()
            try:
                target.relative_to(dest)
            except ValueError:
                fail(f"path escapes site: {relative}")
            if not target.is_file():
                fail(f"missing listed file {relative}")
            listed.append(relative)

    extra = sorted(set(copied) - set(listed))
    if extra:
        fail("program file is not listed in versions.json: " + ", ".join(extra))
    print(f"packed {len(listed)} program file(s) into {dest}")


if __name__ == "__main__":
    main()
