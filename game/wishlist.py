"""Merkliste: Digimon, die ein Spieler erreichen möchte (pro Konto gespeichert).

Im Digimon-Finder merkt man sich ein Ziel, im Spiel zeigt die Merkliste dann den
Weg vom aktuellen Digimon dorthin – mit allen Bedingungen.
"""
from . import data
from .i18n import T

MAX = 20


def _key(owner):
    return f"wishlist:{owner}"


def get(store, owner):
    """Gemerkte Digimon-Nummern (zusammengelegte Nummern werden umgestellt)."""
    out = []
    for dex in store.get_meta(_key(owner), []):
        dex = data.ALIASES.get(dex, dex)
        if dex in data.PLAYABLE and dex not in out:
            out.append(dex)
    return out


def toggle(store, owner, dex, on):
    """Merken (on=True) oder vergessen. Liefert die neue Liste."""
    if dex not in data.PLAYABLE:
        raise ValueError(T("Dieses Digimon gibt es nicht."))
    wanted = get(store, owner)
    if on and dex not in wanted:
        if len(wanted) >= MAX:
            raise ValueError(T("Die Merkliste ist voll – höchstens {n} Digimon.", n=MAX))
        wanted.append(dex)
    elif not on and dex in wanted:
        wanted.remove(dex)
    store.set_meta(_key(owner), wanted)
    return wanted


def set_goal(store, owner, pet, dex):
    """Ziel für genau dieses Digimon (pet["goal"]) – oder None = kein Ziel. Das Ziel bleibt beim
    Digimon (auch in der Sammlung); unter "Nächste Digitation" steht nur noch das eigene Ziel.
    Ein neues Ziel kommt automatisch auf die Merkliste."""
    from . import pet as P
    name = P.label(pet)
    if dex is None:
        pet.pop("goal", None)
        return T("{name} hat jetzt kein Ziel mehr.", name=name)
    if dex not in data.PLAYABLE:
        raise ValueError(T("Dieses Digimon gibt es nicht."))
    if dex not in get(store, owner):
        toggle(store, owner, dex, True)
    pet["goal"] = dex
    return T("Neues Ziel für {name}: {goal}.", name=name, goal=data.PLAYABLE[dex]["name"])
