"""Nach dem Hochladen prüfen, ob die neue Version live ist.

    python tools/dev/check_live.py [suchtext-in-hilfe.html]

Die Live-Adresse steht absichtlich NICHT im Repository, sondern in der lokalen,
git-ignorierten DEPLOY.local.md (erste https://-Adresse dort). Gibt den obersten
Changelog-Eintrag der Live-Seite aus; mit Suchtext zusätzlich, ob er in hilfe.html steht.
"""
import json
import os
import re
import sys
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def live_url():
    try:
        with open(os.path.join(ROOT, "DEPLOY.local.md"), encoding="utf-8") as f:
            m = re.search(r"https://[^\s)>*]+", f.read())
    except OSError:
        m = None
    if not m:
        sys.exit("Keine Live-Adresse gefunden – sie gehört in DEPLOY.local.md (nicht ins Repository).")
    return m.group(0).rstrip("/")


def main():
    base = live_url()
    with urllib.request.urlopen(base + "/changelog.json", timeout=30) as r:
        top = json.load(r)[0]
        print("changelog.json:", r.status, top["version"], "-", top["title"])
    with urllib.request.urlopen(base + "/", timeout=30) as r:
        print("Startseite:", r.status)
    if len(sys.argv) > 1:
        with urllib.request.urlopen(base + "/hilfe.html", timeout=30) as r:
            print("Text in hilfe.html:", sys.argv[1] in r.read().decode("utf-8"))


if __name__ == "__main__":
    main()
