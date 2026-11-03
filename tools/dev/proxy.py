"""Mini-Proxy für Screenshots: meldet den Browser als Testkonto an und spritzt optional ein
Skript in jede HTML-Seite (z. B. "Rucksack öffnen, Item antippen").

    python tools/dev/proxy.py <server-port> <proxy-port> [--lang de|en] [--inject datei.js]

Headless-Browser können kein Cookie setzen – der Proxy hängt "vpet_session=testtoken-tester"
und die Sprache an jede Anfrage. Normalerweise startet ihn screenshot.py selbst.
"""
import http.server
import sys
import urllib.error
import urllib.request


def main():
    args = sys.argv[1:]
    if len(args) < 2:
        sys.exit(__doc__)
    target, port = f"http://127.0.0.1:{args[0]}", int(args[1])
    lang = args[args.index("--lang") + 1] if "--lang" in args else "de"
    script = b"</body>"
    if "--inject" in args:
        with open(args[args.index("--inject") + 1], "rb") as f:
            script = b"<script>" + f.read() + b"</script></body>"
    cookie = f"vpet_session=testtoken-tester; vpet_lang={lang}"

    class Handler(http.server.BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def forward(self, method):
            body = self.rfile.read(int(self.headers.get("Content-Length") or 0)) if method == "POST" else None
            req = urllib.request.Request(target + self.path, data=body, method=method)
            req.add_header("Cookie", cookie)
            if body is not None:
                req.add_header("Content-Type", "application/json")
            try:
                res = urllib.request.urlopen(req)
                code, data, ctype = res.status, res.read(), res.headers.get("Content-Type", "")
            except urllib.error.HTTPError as e:
                code, data, ctype = e.code, e.read(), e.headers.get("Content-Type", "")
            if "text/html" in ctype:
                data = data.replace(b"</body>", script, 1)
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self):
            self.forward("GET")

        def do_POST(self):
            self.forward("POST")

    http.server.ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()


if __name__ == "__main__":
    main()
