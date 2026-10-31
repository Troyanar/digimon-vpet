"""Baut static/digidex.json (deutsch) und static/digidex_en.json (englisch) für den
Digidex auf der Hilfe-Seite.

Quellen:
  data/digidex_api.json   – von tools/fetch_digidex.py (Digi-API, englisch)
  data/digidex_de.json    – deutsche Beschreibungen {Digimon-Nr: Text}
Typen (z. B. "Reptile") werden über TYPES_DE übersetzt; unbekannte bleiben englisch.
Die englische Fassung nimmt die Original-Beschreibungen der Digi-API.

Aufruf:  python tools/build_digidex.py
"""
import json
import re
from pathlib import Path

from build_data import NAME_DE
from fetch_digidex import API_NAMES

ROOT = Path(__file__).resolve().parent.parent
API = ROOT / "data" / "digidex_api.json"
DE = ROOT / "data" / "digidex_de.json"
OWN = ROOT / "data" / "digidex_de_eigene.json"
OWN_EN = ROOT / "data" / "digidex_en_eigene.json"
TYPES = ROOT / "data" / "digidex_types_de.json"
OUT = ROOT / "static" / "digidex.json"
OUT_EN = ROOT / "static" / "digidex_en.json"


def _text_names():
    """Andere Digimon-Namen im Text -> so, wie sie im Spiel heißen (japanische API-Namen wie
    "Tyutyumon" und alte Schreibweisen wie "Growmon"). Längste zuerst ("Growmon X" vor "Growmon")."""
    names = {api: NAME_DE.get(ours, ours) for ours, api in API_NAMES.items()
             if api and api != ours and not api.startswith(ours)}
    names.update(NAME_DE)
    return sorted(names.items(), key=lambda kv: -len(kv[0]))


TEXT_NAMES = _text_names()


def add_api_names(api):
    """Weitere Schreibweisen aus der Digi-API selbst ("DORUgoramon", "EBEmon", "Queenbeemon",
    "Piemon" …) -> so, wie das Digimon im Spiel heißt. X-Antikörper-Einträge zählen nicht
    ("EBEmon (X-Antibody)" ist Ebemon X, im Text meint "EBEmon" aber Ebemon), und ein API-Name,
    der im Spiel ein anderes Digimon ist, wird nie umbenannt."""
    global TEXT_NAMES
    game = {dex: d["name"] for dex, d in json.loads((ROOT / "data" / "digimon.json").read_text(encoding="utf8"))["digimon"].items()}
    taken = set(game.values())
    names = dict(TEXT_NAMES)
    for dex, info in api.items():
        old, ours = info.get("api_name") or "", game.get(dex)
        if ours and old and old != ours and "(" not in old and old not in taken:
            names.setdefault(old, ours)
    TEXT_NAMES = sorted(names.items(), key=lambda kv: -len(kv[0]))


# Namen, die vor einem Bindestrich eine Art meinen ("Demon-species" = Dämonen-Art, nicht Daemon)
SPECIES_WORDS = {"Demon"}


def fix_names(text):
    """Namen ersetzen – aber nicht in „…“ (Attackennamen bleiben, wie sie sind). Auch vor einem
    Bindestrich mit kleinem Wort ("Tyranomon-species" -> "Tyrannomon-species"), nicht aber in
    zusammengesetzten Namen ("Ex-Tyranomon" ist ein eigener Eintrag, "Gokumon-Shibari" eine Attacke)."""
    def fix(part):
        for old, new in TEXT_NAMES:
            # auch mit deutschem Genitiv-s ("Growmons Gebrüll" -> "Growlmons Gebrüll")
            after = r"(?=s?(?![\w-]))" if old in SPECIES_WORDS else r"(?=s?(?!\w))(?!s?-[A-Z])"
            part = re.sub(r"(?<![\w-])" + re.escape(old) + after, new, part)
        return part
    return "".join(p if p.startswith("„") else fix(p) for p in re.split(r"(„[^“]*“)", text))


def main():
    api = json.loads(API.read_text(encoding="utf8"))
    add_api_names(api)
    de = json.loads(DE.read_text(encoding="utf8")) if DE.exists() else {}
    # eigene Texte für Digimon, zu denen die API keine Beschreibung hat
    if OWN.exists():
        for dex, text in json.loads(OWN.read_text(encoding="utf8")).items():
            de.setdefault(dex, text)
    types_de = json.loads(TYPES.read_text(encoding="utf8")) if TYPES.exists() else {}
    out, missing = {}, []
    for dex, info in api.items():
        text = de.get(dex)
        if not text:
            missing.append(info["api_name"])
        out[dex] = {
            "description": fix_names(text or ""),
            "types": [types_de.get(t, t) for t in info["types"]],
            "fields": info["fields"],
            "skills": info["skills"],
            "image": info["image"],
        }
    OUT.write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")), encoding="utf8")
    print(f"{len(out)} Einträge -> {OUT} ({OUT.stat().st_size // 1024} KB); ohne deutsche Beschreibung: {len(missing)}")

    # englisch: Original-Text der API (Namen wie im Spiel), Typen unübersetzt
    # (eigene englische Texte für Digimon, zu denen die API keine Beschreibung hat)
    own_en = json.loads(OWN_EN.read_text(encoding="utf8")) if OWN_EN.exists() else {}
    out_en = {dex: {**entry, "description": fix_names(api[dex].get("description_en") or own_en.get(dex, "")),
                    "types": api[dex]["types"]}
              for dex, entry in out.items()}
    OUT_EN.write_text(json.dumps(out_en, ensure_ascii=False, separators=(",", ":")), encoding="utf8")
    missing_en = [dex for dex, e in out_en.items() if not e["description"]]
    print(f"{len(out_en)} Einträge -> {OUT_EN} ({OUT_EN.stat().st_size // 1024} KB); "
          f"ohne englische Beschreibung: {len(missing_en)}")
    untranslated = sorted({t for info in api.values() for t in info["types"] if t not in types_de})
    if untranslated:
        print("Typen ohne Übersetzung:", ", ".join(untranslated))


if __name__ == "__main__":
    main()
