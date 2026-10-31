"""Kämpfe gegen Freunde (live, zwei Konten).

Ablauf: herausfordern -> der andere nimmt an (oder lehnt ab) -> Runden mit
zwei Phasen:
  "aim":   beide schießen (oben/unten, laden oder Spezialattacke). Sind beide
           Schüsse da, wird gewürfelt, ob sie treffen würden – noch ohne Schaden.
           Wer nicht schießt, schießt nach SHOT_TIMEOUT Sekunden automatisch (schwach).
  "dodge": beide sehen den Ball des anderen kommen und weichen aus (oder nicht).
           Nach DODGE_TIMEOUT Sekunden gilt: nicht ausgewichen. Dann zählt die Runde.
Zeiten hier sind echte Sekunden, nicht Spielminuten.

Ein Kampf ist ein dict wie in der Tabelle `duels`: a/b = Konto-IDs, die
Seiten heißen "a" (wer herausfordert) und "b".
"""
import random

from . import battle, data
from . import pet as P
from .i18n import T, stored, text_of

CHALLENGE_TIMEOUT = 60      # so lange wartet eine Herausforderung auf Antwort
SHOT_TIMEOUT = 25           # dann wird automatisch geschossen
DODGE_TIMEOUT = 10          # dann gilt: nicht ausgewichen
AUTO_SHOT = {"aim": "high", "charge": 0}     # wer nicht schießt
MAX_ROUNDS = 25            # wie bei wilden Digimon (game/battle.py)
SHOW_RESULT = 30            # so lange bleibt das Ergebnis sichtbar
OPEN = ("pending", "active")


def other(side):
    return "b" if side == "a" else "a"


def side_of(duel, user_id):
    return "a" if duel["a"] == user_id else "b"


def _result(now, text, **extra):
    """Ergebnis eines Kampfes – mit englischer Fassung, weil es gespeichert wird."""
    return {"finished": now, "text": str(text), "en": getattr(text, "en", str(text)), **extra}


def _ready(pet, whose):
    """Kann dieses Digimon kämpfen? Sonst Refused mit verständlichem Grund."""
    if not pet:
        raise P.Refused(T("{whose} hat gerade kein Digimon.", whose=whose))
    if pet.get("battle") or pet.get("scout"):
        raise P.Refused(T("{whose} kämpft gerade schon gegen ein wildes Digimon.", whose=whose))
    try:
        battle._can_battle(pet)
    except P.Refused as e:
        raise P.Refused(T("{whose}: {reason}", whose=whose, reason=text_of(e)))


def challenge(store, me, target, my_pet, target_pet, now):
    if target["id"] == me["id"]:
        raise P.Refused(T("Du kannst dich nicht selbst herausfordern."))
    for user in (me, target):
        d = store.latest_duel(user["id"])
        if d and d["status"] in OPEN:
            if user is me:
                raise P.Refused(T("Du bist schon in einem Kampf."))
            raise P.Refused(T("{name} ist schon in einem Kampf.", name=target["name"]))
    _ready(my_pet, T("Dein Digimon"))
    try:
        _ready(target_pet, T("Das Digimon von {name}", name=target["name"]))
    except P.Refused:
        # den Grund (z. B. wann es vom Erkunden zurück ist) behalten wir für uns
        raise P.Refused(T("{name} kann gerade nicht kämpfen.", name=target["name"])) from None
    return store.add_duel(me["id"], target["id"], {
        "created": now, "names": {"a": me["name"], "b": target["name"]},
        "round": 0, "shots": {}, "hp": {}, "max": {}, "rounds": [], "result": None,
    })


def answer(duel, accept, pets, now):
    if duel["status"] != "pending":
        raise P.Refused(T("Diese Herausforderung gilt nicht mehr."))
    if not accept:
        duel["status"] = "declined"
        duel["data"]["result"] = _result(now, T("{name} hat abgelehnt.", name=duel["data"]["names"]["b"]))
        return T("Herausforderung abgelehnt.")
    names = duel["data"]["names"]
    _ready(pets["b"], T("Dein Digimon"))
    try:
        _ready(pets["a"], T("Das Digimon von {name}", name=names["a"]))
    except P.Refused:
        raise P.Refused(T("{name} kann gerade nicht kämpfen.", name=names["a"])) from None
    d = duel["data"]
    for side in ("a", "b"):
        pet = pets[side]
        pet["hunger"] -= 1
        pet["strength"] -= 1
        d["hp"][side] = d["max"][side] = battle.max_hp(pet)
        d.setdefault("pets", {})[side] = pet["id"]
    duel["status"] = "active"
    d["round"] = 1
    d["round_start"] = now
    d["phase"] = "aim"
    d["gauge"] = {"a": 0, "b": 0}
    return T("Der Kampf beginnt!")


def _phase(d):
    return d.get("phase", "aim")          # ältere Kämpfe kennen keine Phasen


def shoot(duel, side, attack, pets, now, rng=random):
    """Schuss einer Seite. `attack`: siehe battle.parse_shot (auch die alte Zahl "quality")."""
    if duel["status"] != "active":
        raise P.Refused(T("Gerade läuft kein Kampf."))
    d = duel["data"]
    if _phase(d) != "aim":
        raise P.Refused(T("Jetzt heißt es ausweichen!"))
    if side in d["shots"]:
        raise P.Refused(T("Du hast schon geschossen – warte auf deinen Gegner."))
    shot = battle.parse_shot(attack)
    if shot["special"] and d.get("gauge", {}).get(side, 0) < battle.SPECIAL_MAX:
        raise P.Refused(T("Deine Spezial-Leiste ist noch nicht voll."))
    d["shots"][side] = shot
    if len(d["shots"]) == 2:
        _roll(duel, pets, now, rng)


def dodge(duel, side, dodged, pets, now, rng=random):
    """Ausweichen (oder nicht) vor dem Ball des Gegners."""
    if duel["status"] != "active":
        raise P.Refused(T("Gerade läuft kein Kampf."))
    d = duel["data"]
    if _phase(d) != "dodge":
        raise P.Refused(T("Gerade fliegt kein Angriff auf dich zu."))
    if side in d["dodges"]:
        raise P.Refused(T("Du hast schon reagiert – warte auf deinen Gegner."))
    d["dodges"][side] = dodged is True
    if len(d["dodges"]) == 2:
        _resolve(duel, pets, now, rng)


def tick(duel, pets, now, rng=random):
    """Zeitüberschreitungen: Herausforderung verfällt, Zögerer schießen automatisch
    bzw. weichen nicht aus."""
    d = duel["data"]
    if duel["status"] == "pending" and now - d["created"] > CHALLENGE_TIMEOUT:
        duel["status"] = "expired"
        d["result"] = _result(now, T("Die Herausforderung ist abgelaufen."))
    elif duel["status"] == "active" and _phase(d) == "aim" and now - d["round_start"] > SHOT_TIMEOUT:
        for side in ("a", "b"):
            d["shots"].setdefault(side, dict(AUTO_SHOT))
        _roll(duel, pets, now, rng)
    elif duel["status"] == "active" and _phase(d) == "dodge" and now - d["round_start"] > DODGE_TIMEOUT:
        for side in ("a", "b"):
            d["dodges"].setdefault(side, False)
        _resolve(duel, pets, now, rng)


def cancel(duel, side, now):
    """Herausforderung zurückziehen – nur solange sie noch nicht angenommen ist
    (sonst würde ein Klick im falschen Moment als Aufgeben zählen)."""
    if duel["status"] != "pending" or side != "a":
        raise P.Refused(T("Zu spät – der Kampf hat schon begonnen!"))
    return forfeit(duel, side, {}, now)


def forfeit(duel, side, pets, now, rng=random):
    """Zurückziehen (vor dem Kampf) oder Aufgeben (im Kampf = Niederlage)."""
    if duel["status"] == "pending":
        duel["status"] = "cancelled"
        duel["data"]["result"] = _result(now, T("Die Herausforderung wurde zurückgezogen."))
        return T("Herausforderung zurückgezogen.")
    if duel["status"] == "active":
        _finish(duel, pets, other(side), now, rng, gave_up=side)
        return T("Du hast aufgegeben.")
    raise P.Refused(T("Gerade läuft kein Kampf."))


def _swapped(duel, pets, now):
    """Wurde ein Digimon getauscht? Dann wird der Kampf abgebrochen."""
    d = duel["data"]
    a, b = pets["a"], pets["b"]
    if not a or not b or d.get("pets", {}).get("a") != a["id"] or d.get("pets", {}).get("b") != b["id"]:
        duel["status"] = "aborted"
        d["result"] = _result(now, T("Kampf abgebrochen – ein Digimon wurde getauscht."))
        return True
    return False


def _roll(duel, pets, now, rng):
    """Beide Schüsse sind da: würfeln, ob sie treffen würden (noch ohne Schaden),
    dann Phase "dodge"."""
    if _swapped(duel, pets, now):
        return
    d = duel["data"]
    d["attacks"], d["incoming"], d["dodges"] = {}, {}, {}
    for side in ("a", "b"):                          # gleichzeitig!
        me, foe = pets[side], pets[other(side)]
        bonus = battle.attr_bonus(battle.attribute(me["dex"]), battle.attribute(foe["dex"]))
        roll = battle.roll_attack(battle.parse_shot(d["shots"][side]), battle.power(me),
                                  battle.power(foe), bonus, rng)
        d["attacks"][side] = roll
        # was auf die andere Seite zufliegt (bei interrupted: nichts)
        d["incoming"][other(side)] = {"side": roll["aim"], "special": roll["special"], "power": roll["power"],
                                      "mega": roll["mega"], "interrupted": roll["interrupted"]}
    for side in ("a", "b"):
        coming = d["incoming"][side]
        if coming["interrupted"] or coming["special"]:   # nichts zum Ausweichen
            d["dodges"][side] = False
    d["phase"] = "dodge"
    d["round_start"] = now
    if len(d["dodges"]) == 2:
        _resolve(duel, pets, now, rng)


def _resolve(duel, pets, now, rng):
    """Beide haben reagiert: Treffer zählen, Leben abziehen, nächste Runde."""
    if _swapped(duel, pets, now):
        return
    d = duel["data"]
    gauge = d.setdefault("gauge", {"a": 0, "b": 0})
    attacks = d["attacks"]
    hits, dodged, damage = {}, {}, {}
    for side in ("a", "b"):
        roll, foe = attacks[side], other(side)
        # foe ist ausgewichen – zählt nur, wenn wirklich etwas Ausweichbares kam
        dodged[foe] = bool(d["dodges"].get(foe)) and not roll["special"] and not roll["interrupted"]
        hits[side] = roll["hit"] and not dodged[foe]
        damage[side] = roll["damage"] if hits[side] else 0
    for side in ("a", "b"):
        if attacks[side]["special"]:
            gauge[side] = 0                          # Spezialattacke leert die Leiste
    for side in ("a", "b"):
        # gegen Freunde füllen EINGESTECKTE Treffer und gelungenes Ausweichen die Leiste – nicht
        # ausgeteilte Treffer, sonst wären beide Leisten immer gleich voll (Spezial gleichzeitig =
        # Unentschieden); nur eingesteckte allein reichen nicht, da ist man vorher k.o.
        if dodged[side]:
            gauge[side] = battle.fill(gauge[side])
        if hits[side]:
            foe = other(side)
            d["hp"][foe] = max(0, d["hp"][foe] - damage[side])
            gauge[foe] = battle.fill(gauge[foe])
    d["rounds"].append({"hit": hits, "power": {s: attacks[s]["power"] for s in ("a", "b")},
                        "hp": dict(d["hp"]),
                        "aim": {s: attacks[s]["aim"] for s in ("a", "b")},
                        "mega": {s: attacks[s]["mega"] for s in ("a", "b")},
                        "special": {s: attacks[s]["special"] for s in ("a", "b")},
                        "interrupted": {s: attacks[s]["interrupted"] for s in ("a", "b")},
                        "dodged": dodged, "damage": damage, "gauge": dict(gauge)})
    d["shots"], d["attacks"], d["incoming"], d["dodges"] = {}, {}, {}, {}
    d["phase"] = "aim"
    d["round"] += 1
    d["round_start"] = now
    over = d["hp"]["a"] <= 0 or d["hp"]["b"] <= 0 or len(d["rounds"]) >= MAX_ROUNDS
    if over:
        if d["hp"]["a"] == d["hp"]["b"]:
            winner = None                                # Unentschieden
        else:
            winner = "a" if d["hp"]["a"] > d["hp"]["b"] else "b"
        _finish(duel, pets, winner, now, rng)


def _finish(duel, pets, winner, now, rng, gave_up=None):
    from . import shop
    d = duel["data"]
    names = d["names"]
    # Bits für beide Seiten (der Server schreibt sie beim Speichern einmal gut); wer aufgibt, bekommt nichts
    d["bits"] = {side: (shop.DUEL["win"] if winner == side else shop.DUEL["draw"] if winner is None
                        else 0 if gave_up == side else shop.DUEL["loss"]) for side in ("a", "b")}
    for side in ("a", "b"):
        pet = pets[side]
        # nur die Digimon, die wirklich gekämpft haben (nicht ein eingewechseltes)
        if not pet or pet["id"] != d.get("pets", {}).get(side):
            continue
        pet.pop("charm", None)
        pet["battles"] += 1
        pet["battles_stage"] += 1
        foe = names[other(side)]
        bits = " " + shop.bits_text(d["bits"][side]) if d["bits"][side] else ""
        if winner == side:
            pet["wins"] += 1
            pet["wins_stage"] += 1
            pet["weight"] = max(P.BASE_WEIGHT[pet["stage"]], pet["weight"] - rng.randint(1, 2))
            P._log(pet, pet["last"], T("{name} hat gegen {opp} gewonnen!", name=P.display_name(pet), opp=foe) + bits)
        elif winner is None:
            P._log(pet, pet["last"], T("Unentschieden gegen {opp}.", opp=foe) + bits)
        else:
            text = T("{name} hat gegen {opp} verloren.", name=P.display_name(pet), opp=foe)
            if rng.random() < battle.injury_chance(pet):
                pet["injured"], pet["injured_since"] = True, pet["last"]
                text += " " + T("Es ist verletzt!")
            P._log(pet, pet["last"], text + bits)
    duel["status"] = "done"
    if gave_up:
        text = T("{loser} hat aufgegeben – {winner} gewinnt!", loser=names[gave_up], winner=names[winner])
    elif winner:
        text = T("{winner} gewinnt den Kampf!", winner=names[winner])
    else:
        text = T("Unentschieden!")
    d["result"] = _result(now, text, winner=winner)


def _round_view(r, me, foe):
    """Eine gespielte Runde aus meiner Sicht (ältere Runden haben nur hit/power/hp)."""
    def both(key, default):
        values = r.get(key) or {}
        return values.get(me, default), values.get(foe, default)
    my_aim, opp_aim = both("aim", "high")
    my_mega, opp_mega = both("mega", False)
    my_special, opp_special = both("special", False)
    my_interrupted, opp_interrupted = both("interrupted", False)
    i_dodged, they_dodged = both("dodged", False)
    my_damage, opp_damage = both("damage", None)
    my_gauge, opp_gauge = both("gauge", 0)
    return {"my_hit": r["hit"][me], "opp_hit": r["hit"][foe], "power_shot": r["power"][me],
            "opp_power": r["power"][foe], "my_hp": r["hp"][me], "opp_hp": r["hp"][foe],
            "my_aim": my_aim, "opp_aim": opp_aim, "my_mega": my_mega, "opp_mega": opp_mega,
            "my_special": my_special, "opp_special": opp_special,
            "my_interrupted": my_interrupted, "opp_interrupted": opp_interrupted,
            "i_dodged": i_dodged, "they_dodged": they_dodged,
            # Schaden: ausgeteilt / eingesteckt (alte Runden: 1 pro Treffer)
            "my_damage": int(r["hit"][me]) if my_damage is None else my_damage,
            "opp_damage": int(r["hit"][foe]) if opp_damage is None else opp_damage,
            "my_gauge": my_gauge, "opp_gauge": opp_gauge}


def view(duel, user_id, pets, now):
    """Der Kampf aus Sicht eines Spielers (oder None, wenn nichts anzuzeigen ist)."""
    if not duel:
        return None
    d = duel["data"]
    if duel["status"] not in OPEN and (not d.get("result") or now - d["result"]["finished"] > SHOW_RESULT):
        return None
    me = side_of(duel, user_id)
    foe = other(me)
    foe_pet = pets.get(foe)
    out = {
        "id": duel["id"], "status": duel["status"], "challenger": me == "a",
        "opponent": d["names"][foe],
        "opp_pet": {"dex": foe_pet["dex"], "name": P.display_name(foe_pet), "stage_de": P.stage_name(foe_pet["stage"]),
                    "attribute": data.DIGIMON[foe_pet["dex"]]["attribute"]} if foe_pet and foe_pet.get("dex") else None,
        "expires_in": max(0, int(CHALLENGE_TIMEOUT - (now - d["created"]))) if duel["status"] == "pending" else None,
        "result": None,
    }
    if duel["status"] == "active" or d["rounds"]:
        phase = _phase(d)
        dodging = duel["status"] == "active" and phase == "dodge"
        gauge = d.get("gauge", {})
        my_pet = pets.get(me)
        mine = d.get("attacks", {}).get(me) if dodging else None
        out.update({
            "round": d["round"], "my_hp": d["hp"].get(me), "opp_hp": d["hp"].get(foe),
            "my_max": d["max"].get(me), "opp_max": d["max"].get(foe),
            "phase": phase,
            "i_shot": me in d["shots"], "they_shot": foe in d["shots"],
            # in Phase "dodge": was auf mich zufliegt und mein eigener Schuss (für die Animation)
            "incoming": dict(d["incoming"][me]) if dodging and d.get("incoming", {}).get(me) else None,
            "my_attack": {k: mine[k] for k in ("aim", "interrupted", "special", "power", "mega")} if mine else None,
            "i_dodged": dodging and me in d.get("dodges", {}),
            "they_dodged": dodging and foe in d.get("dodges", {}),
            "my_gauge": gauge.get(me, 0), "opp_gauge": gauge.get(foe, 0), "special_max": battle.SPECIAL_MAX,
            "special_name": battle.special_name(my_pet["dex"]) if my_pet and my_pet.get("dex") else None,
            "opp_special_name": battle.special_name(foe_pet["dex"]) if foe_pet and foe_pet.get("dex") else None,
            "time_left": max(0, int((DODGE_TIMEOUT if dodging else SHOT_TIMEOUT)
                                    - (now - d.get("round_start", now)))),
            # Runden aus meiner Sicht
            "rounds": [_round_view(r, me, foe) for r in d["rounds"]],
        })
    if d.get("result"):
        res = d["result"]
        out["result"] = {"text": stored(res["text"], res.get("en")),
                         "won": res.get("winner") == me if "winner" in res else None,
                         "draw": "winner" in res and res["winner"] is None}
    return out
