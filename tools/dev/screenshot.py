"""Bildschirmfoto vom laufenden Prüf-Server – als Testkonto, optional nach ein paar Klicks.

    python tools/dev/screenshot.py <ausgabe.png> [--port 8091] [--lang de|en] [--page /hilfe.html]
                                   [--js "press('bag')"] [--size 1300,1000] [--wait 7000]

--js läuft 3 s nach dem Laden (alle Fenster sind dann zu); mehrere Schritte mit ";" und
setTimeout, z. B. --js "press('bag'); setTimeout(() => press('bagitem:virus'), 800)".
In game.js sind u. a. press(id), openFriend(name), openCollection(), openShop() global.
Braucht Microsoft Edge oder Google Chrome. Headless-Edge rendert mindestens ~500 px breit.
Das LCD-Display bleibt im Headless-Bild oft leer – das ist kein Fehler.
"""
import os
import shutil
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
BROWSERS = [r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            shutil.which("msedge") or "", shutil.which("chrome") or "", shutil.which("chromium") or ""]


def opt(args, key, default):
    return args[args.index(key) + 1] if key in args else default


def main():
    args = sys.argv[1:]
    if not args or args[0].startswith("--"):
        sys.exit(__doc__)
    out = os.path.abspath(args[0])
    port, lang = opt(args, "--port", "8091"), opt(args, "--lang", "de")
    page, size, wait = opt(args, "--page", "/"), opt(args, "--size", "1300,1000"), opt(args, "--wait", "7000")
    js = opt(args, "--js", "")
    browser = next((b for b in BROWSERS if b and os.path.exists(b)), None)
    if not browser:
        sys.exit("Kein Edge/Chrome gefunden.")
    tmp = tempfile.mkdtemp(prefix="vpet-shot-")
    inject = os.path.join(tmp, "inject.js")
    with open(inject, "w", encoding="utf-8") as f:
        f.write("setTimeout(() => { document.querySelectorAll('aside').forEach(a => a.hidden = true);"
                f" document.getElementById('scrim') && (document.getElementById('scrim').hidden = true); {js} }}, 3000);")
    proxy_port = str(int(port) + 10)
    proxy = subprocess.Popen([sys.executable, os.path.join(HERE, "proxy.py"), port, proxy_port,
                              "--lang", lang, "--inject", inject])
    time.sleep(1.5)
    try:
        subprocess.run([browser, "--headless=new", "--hide-scrollbars", f"--user-data-dir={tmp}\\profile",
                        f"--window-size={size}", f"--virtual-time-budget={wait}", f"--screenshot={out}",
                        f"http://127.0.0.1:{proxy_port}{page}{'&' if '?' in page else '?'}lang={lang}"],
                       stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL, timeout=180)
    finally:
        proxy.kill()
        shutil.rmtree(tmp, ignore_errors=True)
    print("Bild:", out)


if __name__ == "__main__":
    main()
