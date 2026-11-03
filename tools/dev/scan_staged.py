"""Vor jedem `git commit`/`git push`: gestagte Änderungen auf Dinge prüfen, die nicht in das
öffentliche Repository gehören.

    git add -A
    python tools/dev/scan_staged.py        # Ausgabe "ok" = sauber, sonst Fundstellen + Exit-Code 1

Geprüft werden nur HINZUGEFÜGTE Zeilen. Verboten sind:
- Server-Adressen: alle Hostnamen, IPs und /opt/-Pfade, die in den lokalen, git-ignorierten
  Dateien DEPLOY.local.md und deploy.bat stehen (die Liste steht absichtlich nicht hier im Code);
- persönliche Windows-Pfade (C:\\Users\\…), private Schlüssel, API-Keys/Passwörter im Klartext;
- Dateien, die nie ins Repository gehören (*.db, deploy.bat, DEPLOY.local.md, .env, backups/).
"""
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LOCAL_FILES = ("DEPLOY.local.md", "deploy.bat")
BAD_FILES = re.compile(r"(\.db(-journal|-wal|-shm)?$|(^|/)deploy\.bat$|(^|/)DEPLOY\.local\.md$|(^|/)\.env$|(^|/)backups/|(^|/)state/)")
GENERIC = [r"[A-Za-z]:\\+Users\\+", r"BEGIN [A-Z ]*PRIVATE KEY", r"(?i)api[_-]?key\s*[:=]\s*['\"][^'\"]{8,}",
           r"(?i)password\s*[:=]\s*['\"][^'\"]{4,}"]


def local_secrets():
    """Hostnamen, IPs und Server-Pfade aus den lokalen Deploy-Dateien."""
    words = set()
    for name in LOCAL_FILES:
        try:
            with open(os.path.join(ROOT, name), encoding="utf-8", errors="ignore") as f:
                text = f.read()
        except OSError:
            continue
        words.update(re.findall(r"https?://([A-Za-z0-9.-]+)", text))
        words.update(re.findall(r"\b\d{1,3}(?:\.\d{1,3}){3}\b", text))
        words.update(re.findall(r"/opt/[A-Za-z0-9_./-]+", text))
    return sorted(w for w in words if w not in ("localhost", "127.0.0.1", "0.0.0.0"))


def main():
    git = ["git", "-C", ROOT]
    names = subprocess.run(git + ["diff", "--cached", "--name-only"], capture_output=True, text=True,
                           encoding="utf-8").stdout.split()
    diff = subprocess.run(git + ["diff", "--cached", "-U0"], capture_output=True, text=True,
                          encoding="utf-8", errors="replace").stdout
    patterns = [re.escape(w) for w in local_secrets()] + GENERIC
    found = [f"Datei gehört nicht ins Repository: {n}" for n in names if BAD_FILES.search(n)]
    current = "?"
    for line in diff.splitlines():
        if line.startswith("+++ "):
            current = line[6:] if line.startswith("+++ b/") else line[4:]
        elif line.startswith("+") and not line.startswith("+++"):
            for pat in patterns:
                if current.endswith("tools/dev/scan_staged.py") and pat in GENERIC:
                    continue                                   # die Muster oben selbst
                if re.search(pat, line):
                    found.append(f"{current}: {line[1:].strip()[:120]}")
                    break
    if not names:
        print("Nichts gestagt – erst `git add -A`.")
        return
    if found:
        print("NICHT pushen – bitte entfernen:")
        print("\n".join("  " + f for f in found))
        sys.exit(1)
    print(f"ok – {len(names)} Datei(en) geprüft, nichts Verdächtiges.")


if __name__ == "__main__":
    main()
