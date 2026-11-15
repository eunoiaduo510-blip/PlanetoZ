# Pembuat musik PlanetoZ (abad pertengahan): musik perang dan musik menu, dirakit dari nada dan derau lalu disimpan mp3.
# Pemakaian: python buat_musik.py <folder_keluar>   (butuh: pip install numpy lameenc)
import sys, os
import numpy as np
import lameenc

SR = 44100
OUT = sys.argv[1] if len(sys.argv) > 1 else 'out'
os.makedirs(OUT, exist_ok=True)
rng = np.random.default_rng(88)

NOTE = {'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3, 'E': 4, 'F': 5, 'F#': 6, 'Gb': 6, 'G': 7, 'G#': 8, 'Ab': 8, 'A': 9, 'A#': 10, 'Bb': 10, 'B': 11}


def hz(n):
    """'D4' -> frekuensi"""
    name, octv = n[:-1], int(n[-1])
    return 440.0 * 2 ** ((NOTE[name] + 12 * (octv + 1) - 69) / 12)


def adsr(n, a, d, s, r, sustain_len=None):
    a, d, r = int(a * SR), int(d * SR), int(r * SR)
    sl = max(0, n - a - d - r) if sustain_len is None else sustain_len
    e = np.concatenate([np.linspace(0, 1, max(a, 1), endpoint=False), np.linspace(1, s, max(d, 1), endpoint=False), np.full(sl, s), np.linspace(s, 0, max(r, 1))])
    if len(e) < n:
        e = np.concatenate([e, np.zeros(n - len(e))])
    return e[:n]


def lowpass(x, fc):
    """lowpass 1-kutub dua kali (lewat FFT supaya cepat)"""
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    h = 1 / (1 + (f / fc) ** 4)
    return np.fft.irfft(X * h, len(x))


def bandpass(x, lo, hi):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    h = (1 / (1 + (lo / np.maximum(f, 1)) ** 4)) * (1 / (1 + (f / hi) ** 4))
    return np.fft.irfft(X * h, len(x))


def additive(f, dur, harm, vib=0.0, vibf=5.0, vib_delay=0.15, det=0.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    v = vib * np.clip((t - vib_delay) / 0.3, 0, 1) * np.sin(2 * np.pi * vibf * t + rng.uniform(0, 6))
    ph = 2 * np.pi * np.cumsum(f * (1 + v + det)) / SR
    out = np.zeros(n)
    for k, a in harm:
        if f * k < SR / 2.2:
            out += a * np.sin(k * ph)
    return out


def pluck(f, dur, damp=0.994, bright=0.6):
    """Karplus-Strong (dawai dipetik: kecapi / lute)"""
    n = int(dur * SR)
    p = max(2, int(round(SR / f)))
    init = rng.uniform(-1, 1, p)
    init = bright * init + (1 - bright) * np.convolve(init, np.ones(4) / 4, 'same')
    out = np.zeros(n)
    buf = init.copy()
    i = 0
    while i < n:
        m = min(p, n - i)
        out[i:i + m] = buf[:m]
        nb = damp * 0.5 * (buf + np.roll(buf, -1))
        buf = nb
        i += p
    return out * adsr(n, 0.002, 0.05, 1, 0.08)


def noise(dur):
    return rng.uniform(-1, 1, int(dur * SR))


def place(track, x, t, g=1.0):
    i = int(t * SR)
    if i >= len(track):
        return
    m = min(len(x), len(track) - i)
    track[i:i + m] += x[:m] * g


def reverb(x, seconds=2.2, mix=0.25, damp_hz=4500):
    n_ir = int(seconds * SR)
    t = np.arange(n_ir) / SR
    ir = rng.standard_normal(n_ir) * np.exp(-6.9 * t / seconds)
    ir = lowpass(ir, damp_hz)
    ir[:int(0.012 * SR)] = 0
    ir /= np.sqrt(np.sum(ir ** 2)) + 1e-9
    L = len(x) + n_ir
    nfft = 1 << (L - 1).bit_length()
    wet = np.fft.irfft(np.fft.rfft(x, nfft) * np.fft.rfft(ir, nfft), nfft)[:L]
    dry = np.concatenate([x, np.zeros(n_ir)])
    return dry * (1 - mix) + wet * mix * 1.6


def loopify(x, length_s):
    """ekor setelah titik loop dilipat ke awal, supaya berulang tanpa sambungan"""
    n = int(length_s * SR)
    y = x[:n].copy()
    tail = x[n:]
    m = min(len(tail), n)
    y[:m] += tail[:m]
    return y


def save(name, x, kbps=112):
    x = x / (np.max(np.abs(x)) + 1e-9) * 0.82
    x = np.tanh(x * 1.15) / np.tanh(1.15)   # sedikit lembut di puncak
    x *= 0.82 / np.max(np.abs(x))
    pcm = (np.clip(x, -1, 1) * 32767).astype('<i2').tobytes()
    enc = lameenc.Encoder()
    enc.set_bit_rate(kbps)
    enc.set_in_sample_rate(SR)
    enc.set_channels(1)
    enc.set_quality(2)
    data = enc.encode(pcm) + enc.flush()
    open(os.path.join(OUT, name + '.mp3'), 'wb').write(data)
    print(name, round(len(x) / SR, 1), 's', len(data) // 1024, 'KB')


# ---------- alat musik ----------
HORN = [(1, 1), (2, 0.6), (3, 0.42), (4, 0.25), (5, 0.16), (6, 0.1), (7, 0.05)]
SHAWM = [(1, 0.8), (2, 0.7), (3, 0.55), (4, 0.4), (5, 0.32), (6, 0.2), (7, 0.15), (8, 0.08)]
FLUTE = [(1, 1), (2, 0.18), (3, 0.06)]
STR = [(k, 1 / k) for k in range(1, 14)]


def horn(f, dur):
    x = additive(f, dur + 0.25, HORN, vib=0.005, vibf=5.2)
    x = lowpass(x, 2600)
    return x * adsr(len(x), 0.06, 0.15, 0.85, 0.22)


def shawm(f, dur):
    x = additive(f, dur + 0.15, SHAWM, vib=0.006, vibf=6.0)
    x = bandpass(x, 300, 3600)
    return x * adsr(len(x), 0.03, 0.1, 0.8, 0.12)


def flute(f, dur):
    x = additive(f, dur + 0.3, FLUTE, vib=0.007, vibf=5.0, vib_delay=0.25)
    br = bandpass(noise(dur + 0.3), f * 0.8, f * 3) * 0.08
    x = x + br
    return x * adsr(len(x), 0.08, 0.1, 0.8, 0.28)


def strings(f, dur, cutoff=1400):
    x = additive(f, dur + 0.6, STR, vib=0.003, vibf=4.6) + additive(f, dur + 0.6, STR, vib=0.003, vibf=4.1, det=0.003)
    x = lowpass(x, cutoff) * 0.5
    return x * adsr(len(x), 0.5, 0.3, 0.8, 0.6)


def big_drum(dur=0.9):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = 52 + 60 * np.exp(-t * 18)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 4.2)
    skin = lowpass(noise(dur), 600) * np.exp(-t * 30) * 0.8
    return body + skin


def frame_drum(dur=0.25, accent=1.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = bandpass(noise(dur), 500, 3200) * np.exp(-t * 26)
    x += np.sin(2 * np.pi * 190 * t) * np.exp(-t * 22) * 0.5
    return x * accent


def bell(f, dur=2.5):
    n = int(dur * SR)
    t = np.arange(n) / SR
    out = np.zeros(n)
    for r, a, d in ((1, 1, 1.6), (2.76, 0.45, 0.9), (5.4, 0.25, 0.5), (8.9, 0.1, 0.3)):
        out += a * np.sin(2 * np.pi * f * r * t) * np.exp(-t / d)
    return out * adsr(n, 0.003, 0.01, 1, 0.05)


# ================= MUSIK PERANG =================
# 132 bpm, 4/4, D minor dengan akor A mayor (rasa genting). 32 birama, berulang mulus.
BPM = 132
B = 60 / BPM
BARS = 32
LEN = BARS * 4 * B
T = np.zeros(int((LEN + 4) * SR))
prog = ['Dm', 'Dm', 'C', 'C', 'Bb', 'Bb', 'A', 'A'] * 4
roots = {'Dm': ('D2', 'A2', 'F3'), 'C': ('C2', 'G2', 'E3'), 'Bb': ('Bb1', 'F2', 'D3'), 'A': ('A1', 'E2', 'C#3')}
for bar, ch in enumerate(prog):
    t0 = bar * 4 * B
    r, fifth, third = roots[ch]
    sec = bar // 8   # 0: pembuka, 1: tema, 2: tema tinggi, 3: puncak
    # drone gesek (dua birama sekali)
    if bar % 2 == 0:
        g = 0.16 if sec == 0 else 0.22
        place(T, strings(hz(r), 8 * B, 900), t0, g)
        place(T, strings(hz(fifth), 8 * B, 900), t0, g * 0.8)
        if sec >= 2:
            place(T, strings(hz(third), 8 * B, 1600), t0, 0.12)
    # genderang besar: DUM . . DUM | DUM . DUM .
    for s in ([0, 1.5, 2, 3] if sec > 0 else [0, 2]):
        place(T, big_drum(), t0 + s * B, 0.95 if s in (0, 2) else 0.65)
    # rebana: ketukan 2 dan 4, gulungan di akhir tiap 8 birama
    if sec > 0:
        for s in (1, 3):
            place(T, frame_drum(), t0 + s * B, 0.45)
        if bar % 8 == 7:
            for k in range(8):
                place(T, frame_drum(accent=0.5 + k * 0.07), t0 + 2 * B + k * B / 4, 0.4)
    # petikan dawai (seperdelapan)
    if sec > 0 or bar >= 4:
        pl = [r, r, fifth, r, third, r, fifth, r]
        for k, nn in enumerate(pl):
            nn2 = nn[:-1] + str(int(nn[-1]) + 1)
            place(T, pluck(hz(nn2), B * 0.9, 0.992, 0.7), t0 + k * B / 2, 0.32 if k % 2 == 0 else 0.22)

# melodi: (nada, ketukan). Tema 8 birama, dimainkan terompet tanduk lalu shawm satu oktaf lebih tinggi
theme = [('D4', 1.5), ('E4', 0.5), ('F4', 1), ('A4', 1), ('G4', 1.5), ('F4', 0.5), ('E4', 2),
         ('E4', 1.5), ('F4', 0.5), ('G4', 1), ('C5', 1), ('A4', 2), ('G4', 2),
         ('F4', 1.5), ('G4', 0.5), ('A4', 1), ('Bb4', 1), ('A4', 1.5), ('G4', 0.5), ('F4', 2),
         ('E4', 1), ('F4', 1), ('G4', 1), ('E4', 1), ('A4', 2), ('C#5', 1), ('E4', 1)]


def play(seq, start_bar, inst, oct_shift=0, g=0.5):
    t = start_bar * 4 * B
    for nn, beats in seq:
        f = hz(nn) * 2 ** oct_shift
        place(T, inst(f, beats * B * 0.92), t, g)
        t += beats * B


play(theme, 8, horn, 0, 0.42)
play(theme, 16, shawm, 0, 0.3)
play(theme, 16, horn, -1, 0.22)
play(theme, 24, shawm, 0, 0.32)
play(theme, 24, horn, 0, 0.3)
# seruan terompet pendek di bagian pembuka
for bar in (1, 3, 5):
    t0 = bar * 4 * B + 2 * B
    place(T, horn(hz('A3'), B * 0.45), t0, 0.35)
    place(T, horn(hz('D4'), B * 1.3), t0 + B * 0.5, 0.35)
# simbal / gong kecil di awal tiap bagian
for bar in (0, 8, 16, 24):
    place(T, bell(hz('D3'), 3) * 0.6 + lowpass(noise(3), 6000) * np.exp(-np.arange(int(3 * SR)) / SR * 2.2) * 0.15, bar * 4 * B, 0.35)

W = reverb(T, 2.4, 0.22)
save('perang', loopify(W, LEN))

# ================= MUSIK MENU =================
# 84 bpm, 3/4, D dorian: kecapi berarpeggio, suling kayu, gesek lembut, lonceng jauh. 32 birama.
BPM = 84
B = 60 / BPM
BARS = 32
LEN = BARS * 3 * B
T = np.zeros(int((LEN + 5) * SR))
prog = ['Dm', 'C', 'G', 'Dm', 'F', 'C', 'G', 'Asus'] * 4
chords = {'Dm': ['D3', 'A3', 'D4', 'F4'], 'C': ['C3', 'G3', 'C4', 'E4'], 'G': ['G2', 'D3', 'G3', 'B3'], 'F': ['F2', 'C3', 'F3', 'A3'], 'Asus': ['A2', 'E3', 'A3', 'D4']}
for bar, ch in enumerate(prog):
    t0 = bar * 3 * B
    c = chords[ch]
    arp = [c[0], c[1], c[2], c[3], c[2], c[1]]
    for k, nn in enumerate(arp):
        place(T, pluck(hz(nn), 2.2, 0.9965, 0.45), t0 + k * B / 2, 0.36 if k == 0 else 0.24)
    if bar % 2 == 0:
        place(T, strings(hz(c[0]), 6 * B, 800), t0, 0.12)
        place(T, strings(hz(c[2]), 6 * B, 1200), t0, 0.07)
    if bar % 8 == 0:
        place(T, bell(hz('D5'), 3.5), t0, 0.1)
        place(T, bell(hz('A5'), 3), t0 + 1.5 * B, 0.05)

mel = [('A4', 2), ('D5', 1), ('C5', 1.5), ('B4', 0.5), ('A4', 1), ('G4', 2), ('A4', 1), ('D4', 3),
       ('F4', 2), ('G4', 1), ('A4', 1.5), ('G4', 0.5), ('F4', 1), ('E4', 1), ('D4', 1), ('E4', 1), ('E4', 3)]
mel2 = [('D5', 2), ('E5', 1), ('C5', 2), ('A4', 1), ('B4', 1.5), ('A4', 0.5), ('G4', 1), ('A4', 3),
        ('F4', 1), ('G4', 1), ('A4', 1), ('C5', 2), ('B4', 1), ('G4', 1.5), ('A4', 0.5), ('B4', 1), ('A4', 3)]


def play2(seq, start_bar, inst, g):
    t = start_bar * 3 * B
    for nn, beats in seq:
        place(T, inst(hz(nn), beats * B * 0.95), t, g)
        t += beats * B


play2(mel, 8, flute, 0.34)
play2(mel2, 16, flute, 0.34)
play2(mel, 24, flute, 0.3)
play2([(n[:-1] + str(int(n[-1]) - 1), d) for n, d in mel], 24, strings, 0.1)

W = reverb(T, 3.2, 0.32, 3800)
save('menu', loopify(W, LEN))
