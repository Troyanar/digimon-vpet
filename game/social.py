"""Mit Freunden: Tauschen (Eier & Digimon aus der Sammlung) und Jogress-Anfragen.

Tausch (kann warten, bis der Freund online ist):
    A bietet etwas an -> B nimmt das Geschenk an ODER macht ein Gegenangebot
    (oder lehnt ab) -> A bestätigt den Tausch (oder lehnt ab).
Jogress mit dem Digimon eines Freundes (beide online, wie beim Kampf):
    A fragt -> B stimmt zu -> A's Digimon digitiert, B's Digimon bleibt wie es ist.
"""
from . import collection, data
from . import pet as P
from .i18n import T, stored

JOGRESS_TIMEOUT = 60       # Sekunden


def pet_summary(pet):
    if not pet:
        return None
    if pet.get("stage") == "Egg":
        # Sorte nur bei Event-Eiern (data.egg_name) – sonst heißt es beim Tauschen einfach "Digi-Ei (Ei)"
        return {"id": pet["id"], "name": data.egg_name(pet["line"]), "what": P.stage_name("Egg"), "dex": None}
    return {"id": pet["id"], "name": P.display_name(pet), "what": P.stage_name(pet["stage"]), "dex": pet["dex"]}


def _boxed_pet(store, pet_id, owner):
    """Das Digimon/Ei mit `pet_id`, wenn es in der Sammlung von `owner` liegt."""
    pet = store.pet_by_id(pet_id)
    if not pet or pet["owner"] != str(owner) or pet["active"] or not pet.get("in_box") or not pet.get("alive"):
        return None
    return pet


def _busy(store, pet_id):
    for req in store.db.execute("SELECT id FROM requests WHERE kind='trade' AND status IN ('pending','countered')"):
        r = store.get_request(req[0])
        if pet_id in (r["data"]["offer"], r["data"].get("counter")):
            return True
    return False


# ---------------------------------------------------------------- Tausch

def offer(store, me, target, pet_id, gift):
    if not target or target["id"] == me["id"]:
        raise P.Refused(T("Mit wem willst du tauschen?"))
    pet = _boxed_pet(store, pet_id, me["id"])
    if not pet:
        raise P.Refused(T("Tauschen kannst du nur Eier und Digimon aus deiner Sammlung."))
    collection._trip_check(pet)                     # unterwegs beim Erkunden?
    if _busy(store, pet_id):
        raise P.Refused(T("Das steckt schon in einem anderen Tauschangebot."))
    store.add_request("trade", me["id"], target["id"], {
        "offer": pet_id, "gift": bool(gift), "counter": None,
        "names": {"a": me["name"], "b": target["name"]},
    })
    if gift:
        return T("{pet} an {name} verschenkt. {name} sieht es in der Sammlung.",
                 pet=pet_summary(pet)["name"], name=target["name"])
    return T("{pet} an {name} zum Tausch angeboten. {name} sieht es in der Sammlung.",
             pet=pet_summary(pet)["name"], name=target["name"])


def _req_for(store, req_id, user_id, kind="trade"):
    req = store.get_request(req_id)
    if not req or req["kind"] != kind or user_id not in (req["a"], req["b"]):
        raise P.Refused(T("Dieses Angebot gibt es nicht."))
    return req


def accept_gift(store, me, req_id):
    req = _req_for(store, req_id, me["id"])
    if req["b"] != me["id"] or req["status"] != "pending" or not req["data"]["gift"]:
        raise P.Refused(T("Das ist kein Geschenk an dich."))
    pet = _boxed_pet(store, req["data"]["offer"], req["a"])
    if not pet:
        req["status"] = "failed"
        store.save_request(req)
        raise P.Refused(T("Das Geschenk ist leider nicht mehr da."))
    collection._trip_check(pet)
    if len(collection.boxed(store, str(me["id"]))) >= collection.BOX_SIZE:
        raise P.Refused(T("Deine Sammlung ist voll. Lass erst eins frei."))
    store.move_pet(pet["id"], str(me["id"]))
    req["status"] = "done"
    store.save_request(req)
    return T("{pet} ist jetzt in deiner Sammlung. Danke, {name}!",
             pet=pet_summary(pet)["name"], name=req["data"]["names"]["a"])


def counter(store, me, req_id, pet_id):
    req = _req_for(store, req_id, me["id"])
    if req["b"] != me["id"] or req["status"] != "pending":
        raise P.Refused(T("Auf dieses Angebot kannst du nicht mehr antworten."))
    pet = _boxed_pet(store, pet_id, me["id"])
    if not pet:
        raise P.Refused(T("Anbieten kannst du nur Eier und Digimon aus deiner Sammlung."))
    collection._trip_check(pet)
    if _busy(store, pet_id):
        raise P.Refused(T("Das steckt schon in einem anderen Tauschangebot."))
    req["status"] = "countered"
    req["data"]["counter"] = pet_id
    store.save_request(req)
    return T("Gegenangebot {pet} geschickt. {name} muss noch bestätigen.",
             pet=pet_summary(pet)["name"], name=req["data"]["names"]["a"])


def confirm(store, me, req_id):
    req = _req_for(store, req_id, me["id"])
    if req["a"] != me["id"] or req["status"] != "countered":
        raise P.Refused(T("Hier gibt es nichts zu bestätigen."))
    mine = _boxed_pet(store, req["data"]["offer"], req["a"])
    theirs = _boxed_pet(store, req["data"]["counter"], req["b"])
    if not mine or not theirs:
        req["status"] = "failed"
        store.save_request(req)
        raise P.Refused(T("Der Tausch klappt nicht mehr – eins davon ist nicht mehr in der Sammlung."))
    collection._trip_check(mine)
    collection._trip_check(theirs)
    store.move_pet(mine["id"], str(req["b"]))
    store.move_pet(theirs["id"], str(req["a"]))
    req["status"] = "done"
    store.save_request(req)
    return T("Getauscht! {pet} ist jetzt in deiner Sammlung.", pet=pet_summary(theirs)["name"])


def decline(store, me, req_id):
    req = _req_for(store, req_id, me["id"])
    if req["status"] not in ("pending", "countered"):
        raise P.Refused(T("Dieses Angebot ist schon erledigt."))
    req["status"] = "cancelled" if me["id"] == req["a"] else "declined"
    store.save_request(req)
    return T("Angebot zurückgezogen.") if me["id"] == req["a"] else T("Angebot abgelehnt.")


def trades_view(store, me):
    """Offene Tauschangebote aus Sicht von `me`, mit dem, was zu tun ist."""
    out = []
    for req in store.requests_for(me["id"], "trade", ("pending", "countered")):
        d = req["data"]
        incoming = req["b"] == me["id"]
        offered, countered = store.pet_by_id(d["offer"]), store.pet_by_id(d["counter"]) if d["counter"] else None
        if incoming and req["status"] == "pending":
            todo = "answer"           # annehmen (Geschenk) / Gegenangebot / ablehnen
        elif not incoming and req["status"] == "countered":
            todo = "confirm"          # bestätigen / ablehnen
        else:
            todo = "wait"
        out.append({"id": req["id"], "incoming": incoming, "status": req["status"], "gift": d["gift"],
                    "partner": d["names"]["a" if incoming else "b"], "todo": todo,
                    "offer": pet_summary(offered), "counter": pet_summary(countered)})
    return out


# ---------------------------------------------------------------- Jogress mit Freunden

def jogress_ask(store, me, target, my_pet, to_dex, partner, now):
    if not target or target["id"] == me["id"]:
        raise P.Refused(T("Mit wem willst du fusionieren?"))
    if not any(e["to"] == to_dex and P.partner_fits(need, my_pet, partner) for e, need in P.jogress_options(my_pet)):
        raise P.Refused(T("Das Digimon von {name} passt nicht zu dieser Fusion.", name=target["name"]))
    for req in store.requests_for(me["id"], "jogress", ("pending",)) + \
            store.requests_for(target["id"], "jogress", ("pending",)):
        if now - req["data"]["created"] < JOGRESS_TIMEOUT:
            raise P.Refused(T("Es läuft schon eine Jogress-Anfrage."))
        req["status"] = "expired"
        store.save_request(req)
    store.add_request("jogress", me["id"], target["id"], {
        "to": to_dex, "created": now, "names": {"a": me["name"], "b": target["name"]},
        "pets": {"a": my_pet["id"], "b": partner["id"]},
    })
    return T("Anfrage an {name} geschickt. Warte auf Zustimmung ...", name=target["name"])


def jogress_answer(store, me, accept, pets, now):
    """B antwortet. `pets` = aktive Digimon {"a": ..., "b": ...}. Liefert die Meldung."""
    reqs = [r for r in store.requests_for(me["id"], "jogress", ("pending",)) if r["b"] == me["id"]]
    if not reqs or now - reqs[0]["data"]["created"] > JOGRESS_TIMEOUT:
        raise P.Refused(T("Die Anfrage ist schon abgelaufen."))
    req = reqs[0]
    d = req["data"]
    if not accept:
        req["status"] = "declined"
        store.save_request(req)
        return T("Jogress abgelehnt.")
    a, b = pets["a"], pets["b"]
    if not a or not b or a["id"] != d["pets"]["a"] or b["id"] != d["pets"]["b"]:
        req["status"] = "failed"
        store.save_request(req)
        raise P.Refused(T("Die Fusion klappt nicht mehr – ein Digimon wurde getauscht."))
    message = P.jogress(a, d["to"], b, d["names"]["b"], a["last"])
    P._log(b, b["last"], T("{name} hat {friend} bei einer Jogress geholfen!",
                           name=P.display_name(b), friend=d["names"]["a"]))
    req["status"] = "done"
    d["result"] = str(message)
    d["result_en"] = message.en           # wird gespeichert – englische Fassung mitnehmen
    store.save_request(req)
    return T("Geschafft! {message}", message=message)


def jogress_view(store, me, now):
    """Laufende Jogress-Anfrage (gesendet oder bekommen)."""
    # nur die letzten paar – ältere sind sowieso längst abgelaufen
    for req in store.requests_for(me["id"], "jogress", ("pending", "done", "declined", "failed"), limit=3):
        d = req["data"]
        age = now - d["created"]
        if req["status"] == "pending" and age > JOGRESS_TIMEOUT:
            req["status"] = "expired"
            store.save_request(req)
            continue
        if req["status"] != "pending" and age > JOGRESS_TIMEOUT + 30:
            continue
        incoming = req["b"] == me["id"]
        return {"id": req["id"], "status": req["status"], "incoming": incoming,
                "partner": d["names"]["a" if incoming else "b"],
                "to": data.DIGIMON[d["to"]]["name"], "to_dex": d["to"],
                "expires_in": max(0, int(JOGRESS_TIMEOUT - age)),
                "result": stored(d["result"], d.get("result_en")) if d.get("result") else None}
    return None
