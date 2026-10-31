"""Tests für das Weichmachen der Soundeffekte.  Starten mit:  python -m unittest"""
import array
import io
import unittest
import wave

from tools.soften_sounds import _read, notes, soften

RATE = 44100


def square(parts):
    """Rechteckwelle aus [(frequenz, sekunden)] – wie die Original-Sounds."""
    out = []
    for freq, secs in parts:
        half = RATE / freq / 2
        out += [int(0.6 * 32767) if int(i / half) % 2 == 0 else -int(0.6 * 32767) for i in range(int(secs * RATE))]
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes(array.array("h", out).tobytes())
    return buf.getvalue()


class SoftenTest(unittest.TestCase):
    def test_lower_quieter_same_length(self):
        original = square([(2000, 0.1), (4000, 0.1)])
        soft = soften(original)
        before, _ = _read(original)
        after, _ = _read(soft)
        self.assertEqual(len(before), len(after))                     # Timing bleibt
        self.assertLessEqual(max(abs(x) for x in after), 0.31 * 32767)   # leiser
        tones = [round(f) for _, _, f in notes(before, RATE)]
        self.assertEqual(len(tones), 2)
        # Melodie bleibt (zweiter Ton eine Oktave über dem ersten), aber alles tiefer
        seg = after[int(0.13 * RATE):int(0.17 * RATE)]
        crossings = sum(1 for a, b in zip(seg, seg[1:]) if (a < 0) != (b < 0))
        high = crossings / 2 / (len(seg) / RATE)
        self.assertLess(high, 2200)
        seg = after[int(0.03 * RATE):int(0.07 * RATE)]
        low = sum(1 for a, b in zip(seg, seg[1:]) if (a < 0) != (b < 0)) / 2 / (len(seg) / RATE)
        self.assertAlmostEqual(high / low, 2.0, delta=0.1)


if __name__ == "__main__":
    unittest.main()
