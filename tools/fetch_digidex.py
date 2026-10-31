"""Holt Digidex-Daten (Beschreibung, Typ, Attacken, Felder, Artwork) von der Digi-API
(https://digi-api.com) für alle Digimon im Spiel und speichert sie in
data/digidex_api.json. Daraus baut tools/build_digidex.py die deutsche Fassung.

Aufruf:  python tools/fetch_digidex.py
Bereits geholte Digimon werden übersprungen (Datei wird fortgeschrieben).

Die API schreibt Namen oft japanisch und mit Leerzeichen ("War Greymon", "Piyomon").
Deshalb wird erst die ganze Namensliste geholt und ohne Leerzeichen/Satzzeichen
verglichen; für englische Namen hilft API_NAMES.
"""
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GAME = ROOT / "data" / "digimon.json"
OUT = ROOT / "data" / "digidex_api.json"
API = "https://digi-api.com/api/v1/digimon"

# Unsere (englischen) Namen -> japanische Namen in der Digi-API
API_NAMES = {
    "Biyomon": "Piyomon", "Veemon": "V-mon", "DemiVeemon": "Chibimon", "Chibomon": "Chicomon", "XVeemon": "XV-mon",
    "Veedramon": "V-dramon", "AeroVeedramon": "AeroV-dramon", "UlforceVeedramon": "UlforceV-dramon",
    "Tyrannomon": "Tyranomon", "DarkTyrannomon": "DarkTyranomon", "MetalTyrannomon": "MetalTyranomon",
    "ExTyrannomon": "ExTyranomon", "RustTyrannomon": "RustTyranomon", "MasterTyrannomon": "MasterTyranomon",
    "Salamon": "Plotmon", "Gatomon": "Tailmon", "Yokomon": "Pyokomon", "DemiDevimon": "PicoDevimon",
    "Penguinmon": "Penmon", "Syakomon": "Shakomon", "Centarumon": "Centalmon", "Frigimon": "Yukidarumon",
    "PlatinumSukamon": "PlatinumScumon", "Sukamon": "Scumon", "KingSukamon": "KingScumon", "Piximon": "Piccolomon",
    "ShogunGekomon": "TonosamaGekomon", "Mammothmon": "Mammon", "SkullMammothmon": "SkullMammon",
    "MarineDevimon": "MarinDevimon", "MarineAngemon": "MarinAngemon", "Divermon": "Hangyomon",
    "Cherrymon": "Jureimon", "Phantomon": "Fantomon", "MetalPhantomon": "MetalFantomon",
    "SkullMeramon": "DeathMeramon", "MagnaAngemon": "HolyAngemon", "MegaKabuterimon": "AtlurKabuterimon (Red)",
    "Deramon": "Delumon", "Rapidmon": "Rapidmon (Perfect)", "WarGrowmon": "WarGrowlmon", "Growmon": "Growlmon",
    "VenomMyotismon": "VenomVamdemon", "Myotismon": "Vamdemon", "MaloMyotismon": "BelialVamdemon",
    "NeoMyotismon": "BelialVamdemon", "Omnimon": "Omegamon", "Omnimon Alter-S": "Omegamon Alter-S",
    "Cherubimon": "Cherubimon (Virtue)", "MegaGargomon": "SaintGalgomon", "Gargomon": "Galgomon",
    "Gallantmon": "Dukemon", "ChaosGallantmon": "ChaosDukemon", "Crusadermon": "LoadKnightmon",
    "Imperialdramon": "Imperialdramon Fighter Mode", "Imperialdramon PM": "Imperialdramon Paladin Mode",
    "Magnadramon": "Holydramon", "Ophanimon": "Ofanimon", "Lilymon": "Lilimon", "Phoenixmon": "Hououmon",
    "Machinedramon": "Mugendramon", "Piedmon": "Piemon", "Puppetmon": "Pinochimon", "Datamon": "Nanomon",
    "Wizarmon": "Wizarmon", "Pumpmon": "Pumpmon", "NoblePumpmon": "NoblePumpmon", "Bukamon": "Pukamon",
    "Motimon": "Mochimon", "Tortamon": "Tortomon", "Kokatorimon": "Cockatrimon", "Gekomon": "Gekomon",
    "Chakmon": "Chackmon", "BlackKingNumemon": "BlackKingNumemon", "Diaboromon": "Diablomon",
    "Lucemon FM": "Lucemon Falldown Mode", "Craniumon": "Craniummon", "Belphemon": "Belphemon Rage Mode",
    "Arkadimon II": "Arcadiamon (In-Training)", "Arkadimon IV": "Arcadiamon (Champion)",
    "Arkadimon V": "Arcadiamon (Ultimate)", "Arkadimon VI": "Arcadiamon (Super Ultimate)",
    "Milleniumon": "Millenniummon", "MoonMilleniumon": "Moon=Millenniummon", "ZeedMilleniumon": "ZeedMillenniummon",
    "Matadormon": "Matadrmon", "GranDracmon": "GranDracmon", "Dracmon": "Dracmon", "Fanbeemon": "Funbeemon",
    "Shawjinmon": "Shawujinmon", "Boltboutamon": "Boltboutamon", "QueenChessmon": "QueenChessmon",
    "ReverseWeddinmon": "Weddinmon", "Chuchumon": "Chuchumon", "Vemmon": "Vemmon", "TyrantKabuterimon": "TyrantKabuterimon",
    "Kogamon": "Kogamon", "Stefilmon": "Stiffilmon", "MarinChimairamon": "MarinChimairamon",
    "JagerLoweemon": "JagerLowemon", "JagerDorulumon": "JagerDorulumon", "ChoHakkaimon": "Chohakkaimon",
    "Algomon I": "Algomon (Baby I)", "Algomon II": "Algomon (Baby II)", "TorikaraBallmon": "TorikaraBallmon",
    "AgumonHakase": "Agumon -Yuki no Kizuna-", "BushiAgumon": "BushiAgumon", "FrosVelgrmon": "FrosVelgrmon",
    "Rockmon": "Rockmon", "Tinmon": "Tinmon", "GreyKnightsmon": "GreyKnightsmon", "Kiryu": "Kiryuu",
    "Pichimon": "Pitchmon", "DemiMeramon": "Peti Meramon", "Kapurimon": "Caprimon", "Gotsumon": "Gottsumon",
    "Candlemon": "Candmon", "Tsukaimon": "Tukaimon", "Ogremon": "Orgemon", "Flarerizamon": "Flare Lizamon",
    "Octomon": "Octmon", "Jagamon": "Jyagamon", "DoruGreymon": "DORUguremon", "GrapLeomon": "Grappu Leomon",
    "HerculesKabuterimon": "Herakle Kabuterimon", "Beelzemon": "Beelzebumon", "ZeedGarurumon": "Z'd Garurumon",
    "Vermilimon": "Vermillimon", "Gaiomon": "Gaioumon", "Dracmon": "Dracumon", "GranDracmon": "Grand Dracumon",
    "Kogamon": "Kougamon", "Milleniumon": "Millenniumon", "MoonMilleniumon": "Moon Millenniumon",
    "ZeedMilleniumon": "Zeed Millenniumon", "Boltboutamon": "Voltobautamon", "BanchoLilymon": "Bancho Lilimon",
    "KingSukamon": "Great King Sukamon", "JagerDorulumon": "Yaeger Dorulumon", "Tsunomon": "Tunomon",
    "Arkadimon II": "Arkadimon Baby", "Arkadimon IV": "Arkadimon Adult", "Arkadimon V": "Arkadimon Perfect",
    "Arkadimon VI": "Arkadimon Ultimate", "WarGrowmon": "Megalo Growmon", "Crusadermon": "Lord Knightmon",
    "Meteormon": "Insekimon", "Cherrymon": "Jyureimon", "Garbamon": "Gerbemon", "Yokomon": "Pyocomon",
    # vom Spieler ergänzt
    "Apemon": "Hanumon", "Deputymon": "Revolmon", "Beastmon": "Bastemon", "Tinmon": "Blikmon",
    "Reapermon": "Gokumon", "Chuchumon": "Tyutyumon", "Chuumon": "Tyumon", "Rockmon": "Golemon (PS)",
    "JagerLoweemon": "Kaiser Leomon", "Yaamon": "Yarmon", "Kiimon": "Keemon", "ShellNumemon": "Karatuki Numemon",
    "Vemmon": "BEMmon",
    # Armor-Digimon (Adventure 02)
    "Flamedramon": "Fladramon", "Raidramon": "Lighdramon", "Halsemon": "Holsmon", "Pegasusmon": "Pegasmon",
    "Armadillomon": "Armadimon",
}

ALL = []   # [(id, name)] aus der API


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "digimon-vpet (privates Fan-Projekt)"})
    try:
        with urllib.request.urlopen(req, timeout=30) as res:
            return json.loads(res.read().decode("utf8"))
    except urllib.error.HTTPError as e:
        if e.code in (400, 404):
            return None
        raise


def norm(name):
    return re.sub(r"[^a-z0-9]", "", name.lower())


def load_names():
    page = 0
    while True:
        data = get(f"{API}?pageSize=500&page={page}")
        items = (data or {}).get("content") or []
        if not items:
            break
        ALL.extend((it["id"], it["name"]) for it in items)
        page += 1
        time.sleep(0.2)
    print(len(ALL), "Namen in der API")


def find_id(name):
    """Unser Name -> API-Id (exakt, sonst ohne Klammer-Zusatz, X-Varianten über "(X-Antibody)")."""
    base, x_variant = (name[:-2], True) if name.endswith(" X") else (name, False)
    wanted = [API_NAMES.get(name), API_NAMES.get(base), base, name]
    full = {norm(n): i for i, n in ALL}
    plain = {}
    for i, n in ALL:
        plain.setdefault(norm(re.sub(r"\s*\(.*?\)", "", n)), i)
    for w in dict.fromkeys(x for x in wanted if x):
        if x_variant and norm(w + "xantibody") in full:
            return full[norm(w + "xantibody")]
        if not x_variant and norm(w) in full:
            return full[norm(w)]
    for w in dict.fromkeys(x for x in wanted if x):
        if norm(w) in plain:
            return plain[norm(w)]
    return None


def pick(entry):
    """Nur das, was das Digidex braucht."""
    desc = next((d["description"] for d in entry.get("descriptions", []) if d.get("language") == "en_us"), "")
    return {
        "api_id": entry["id"], "api_name": entry["name"],
        "image": (entry.get("images") or [{}])[0].get("href"),
        "types": [t["type"] for t in entry.get("types", [])],
        "levels": [lv["level"] for lv in entry.get("levels", [])],
        "attributes": [a["attribute"] for a in entry.get("attributes", [])],
        "fields": [f["field"] for f in entry.get("fields", [])],
        "skills": [s["skill"] for s in entry.get("skills", [])],
        "description_en": desc,
    }


def main():
    game = json.loads(GAME.read_text(encoding="utf8"))
    playable = sorted({e["to"] for e in game["evolutions"]})
    out = json.loads(OUT.read_text(encoding="utf8")) if OUT.exists() else {}
    load_names()
    missing = []
    for dex in playable:
        key = str(dex)
        if key in out:
            continue
        name = game["digimon"][key]["name"]
        api_id = find_id(name)
        entry = get(f"{API}/{api_id}") if api_id else None
        time.sleep(0.15)                          # die API nicht überlasten
        if entry:
            out[key] = pick(entry)
        else:
            missing.append(name)
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf8")
    print(f"{len(out)} von {len(playable)} gefunden. Nicht gefunden ({len(missing)}): {', '.join(missing)}")


if __name__ == "__main__":
    main()
