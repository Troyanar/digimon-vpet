"""Macht die Soundeffekte ohrenfreundlich.

Die Original-Sounds (aus tuipet) sind reine Rechteckwellen bei 1–5 kHz, voll
ausgesteuert – das klingt quietschig und tut im Kopfhörer weh. Dieses Werkzeug
liest aus jedem Sound die Melodie aus (welche Töne, wie lange) und spielt sie neu:
eine Oktave tiefer, mit weicher Wellenform, sanft ein-/ausgeblendet und leiser.
Längen und Rhythmus bleiben gleich (die Animationen sind darauf abgestimmt).

Aufruf:  python tools/soften_sounds.py <ordner-mit-originalen> <zielordner>
Achtung: immer von den ORIGINALEN ausgehen – zweimal angewendet wird alles noch
eine Oktave tiefer. tools/build_data.py macht das beim Kopieren automatisch.
"""
import array
import io
import math
import sys
import wave
from pathlib import Path

PITCH = 0.5          # mindestens eine Oktave tiefer ...
MAX_FREQ = 2100      # ... und so viele weitere, bis der höchste Ton darunter liegt
                     # (der ganze Sound gemeinsam, damit die Melodie erhalten bleibt)
LEVEL = 0.30         # Spitzenpegel (Original: 0.6 als Rechteck)
HARMONICS = (1.0, 0.30, 0.12)   # fast Sinus, mit etwas Wärme
ATTACK = 0.004       # Sekunden
RELEASE = 0.012


def _read(data):
    with wave.open(io.BytesIO(data)) as w:
        ch, width, rate, n = w.getnchannels(), w.getsampwidth(), w.getframerate(), w.getnframes()
        raw = w.readframes(n)
    if width == 2:
        samples = array.array("h", raw)
    elif width == 1:
        samples = array.array("h", [(b - 128) << 8 for b in raw])
    else:
        raise ValueError(f"{width * 8}-bit wird nicht unterstützt")
    if ch == 2:
        samples = samples[::2]
    return samples, rate


def notes(samples, rate):
    """Zerlegt eine Rechteckwelle in Töne: [(start, ende, frequenz)] in Samples."""
    peak = max((abs(x) for x in samples), default=0)
    if not peak:
        return []
    quiet = 0.1 * peak
    # gleichartige Abschnitte: +, - oder still
    runs, start = [], 0
    kind = lambda x: 0 if abs(x) < quiet else (1 if x > 0 else -1)
    for i in range(1, len(samples) + 1):
        if i == len(samples) or kind(samples[i]) != kind(samples[start]):
            runs.append((kind(samples[start]), start, i - start))
            start = i
    out, cur = [], None          # cur = [start, ende, summe_halbperioden, anzahl]
    for k, s, length in runs:
        if k == 0:
            if length > rate * 0.002 and cur:      # echte Pause beendet den Ton
                out.append(cur)
                cur = None
            continue
        if cur and abs(length - cur[2] / cur[3]) <= 0.25 * cur[2] / cur[3] + 1:
            cur[1], cur[2], cur[3] = s + length, cur[2] + length, cur[3] + 1
        else:
            if cur:
                out.append(cur)
            cur = [s, s + length, length, 1]
    if cur:
        out.append(cur)
    result = []
    for s, e, total, count in out:
        if count < 3:
            # Splitter (Übergänge, einzelne Samples): an den Vorgänger hängen oder weglassen
            if result and result[-1][1] >= s - 2:
                result[-1] = (result[-1][0], e, result[-1][2])
            continue
        result.append((s, e, rate / (2 * total / count)))
    return result


def render(note_list, length, rate):
    out = [0.0] * length
    norm = sum(HARMONICS)
    shift = PITCH
    while note_list and max(f for _, _, f in note_list) * shift > MAX_FREQ:
        shift /= 2
    for s, e, freq in note_list:
        f = freq * shift
        n = e - s
        a, r = max(1, int(ATTACK * rate)), max(1, min(int(RELEASE * rate), n // 3))
        step = 2 * math.pi * f / rate
        for i in range(n):
            env = min(1.0, i / a, (n - i) / r)
            p = step * i
            out[s + i] += env * sum(h * math.sin(k * p) for k, h in enumerate(HARMONICS, 1)) / norm
    return out


def soften(data):
    """WAV-Bytes rein, weiche WAV-Bytes raus (gleiche Länge, 16 bit mono)."""
    samples, rate = _read(data)
    wave_out = render(notes(samples, rate), len(samples), rate)
    top = max((abs(x) for x in wave_out), default=0) or 1
    pcm = array.array("h", (int(x / top * LEVEL * 32767) for x in wave_out))
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(pcm.tobytes())
    return buf.getvalue()


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    src, dst = Path(sys.argv[1]), Path(sys.argv[2])
    dst.mkdir(parents=True, exist_ok=True)
    for f in sorted(src.glob("*.wav")):
        (dst / f.name).write_bytes(soften(f.read_bytes()))
        print("weich gemacht:", f.name)


if __name__ == "__main__":
    main()
