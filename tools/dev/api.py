"""Die Spiel-API direkt aufrufen – als Testkonto, ohne Browser.

    python tools/dev/api.py GET  /api/state            [--port 8091] [--lang en]
    python tools/dev/api.py POST /api/item '{"item": "virus"}'

Oder in eigenen Prüf-Skripten:  from api import call;  call("/api/state")

Wichtig: PowerShell-Invoke-RestMethod schickt den Cookie-Header nicht mit – deshalb hier
urllib. Fehler (400 …) kommen als JSON mit "error" zurück statt als Exception.
"""
import json
import sys
import urllib.error
import urllib.request

COOKIE = "vpet_session=testtoken-tester"       # aus make_test_db.py


def call(path, body=None, port=8091, lang="de"):
    # Git-Bash macht aus "/api/state" gern "C:/Program Files/Git/api/state" – zurückbiegen
    if "/api/" not in path and "api/" in path:
        path = "/" + path[path.index("api/"):]
    elif "/api/" in path:
        path = path[path.index("/api/"):]
    req = urllib.request.Request(
        f"http://127.0.0.1:{port}{path}",
        data=json.dumps(body).encode() if body is not None else None,
        headers={"Cookie": f"{COOKIE}; vpet_lang={lang}", "Content-Type": "application/json"})
    try:
        return json.load(urllib.request.urlopen(req, timeout=30))
    except urllib.error.HTTPError as e:
        return json.load(e)


def main():
    args = sys.argv[1:]
    opts = {"port": 8091, "lang": "de"}
    for key in ("port", "lang"):
        if f"--{key}" in args:
            i = args.index(f"--{key}")
            opts[key] = int(args[i + 1]) if key == "port" else args[i + 1]
            del args[i:i + 2]
    if len(args) < 2:
        sys.exit(__doc__)
    method, path = args[0].upper(), args[1]
    body = json.loads(args[2]) if len(args) > 2 else ({} if method == "POST" else None)
    print(json.dumps(call(path, body, **opts), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
