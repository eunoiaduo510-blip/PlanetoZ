# Pembuat efek suara PlanetoZ bagian 2 (kejadian kerajaan, diplomasi, dagang): dirakit dari nada dan derau, disimpan mp3.
# Pemakaian: python buat_sfx2.py <folder_keluar>   (butuh: pip install numpy lameenc)
import sys, os
import numpy as np
import lameenc

SR = 44100
OUT = sys.argv[1] if len(sys.argv) > 1 else 'out'
os.makedirs(OUT, exist_ok=True)
rng = np.random.default_rng(89)
NOTE = {'C': 0, 'C#': 1, 'D': 2, 'D#': 3, 'Eb': 3, 'E': 4, 'F': 5, 'F#': 6, 'G': 7, 'G#': 8, 'A': 9, 'Bb': 10, 'B': 11}


def hz(n):
    return 440.0 * 2 ** ((NOTE[n[:-1]] + 12 * (int(n[-1]) + 1) - 69) / 12)


def T(sec):
    return np.zeros(int(sec * SR))


def place(tr, x, t, g=1.0):
    i = int(t * SR)
    m = min(len(x), len(tr) - i)
    if m > 0:
        tr[i:i + m] += x[:m] * g


def env(n, a, r_from_end):
    e = np.ones(n)
    na, nr = max(1, int(a * SR)), max(1, int(r_from_end * SR))
    e[:na] = np.linspace(0, 1, na)
    e[-nr:] *= np.linspace(1, 0, nr)
    return e


def filt(x, lo=None, hi=None):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    h = np.ones_like(f)
    if hi:
        h /= 1 + (f / hi) ** 4
    if lo:
        h /= 1 + (lo / np.maximum(f, 1)) ** 4
    return np.fft.irfft(X * h, len(x))


def noise(sec):
    return rng.uniform(-1, 1, int(sec * SR))


def additive(f, sec, harm, vib=0.0, vibf=5.0):
    n = int(sec * SR)
    t = np.arange(n) / SR
    v = vib * np.clip((t - 0.12) / 0.3, 0, 1) * np.sin(2 * np.pi * vibf * t)
    ph = 2 * np.pi * np.cumsum(f * (1 + v)) / SR
    return sum(a * np.sin(k * ph) for k, a in harm if f * k < SR / 2.2)


HORN = [(1, 1), (2, 0.6), (3, 0.42), (4, 0.25), (5, 0.16), (6, 0.1), (7, 0.05)]
STR = [(k, 1 / k) for k in range(1, 12)]


def horn(note, sec, g=1.0):
    x = filt(additive(hz(note), sec + 0.2, HORN, 0.005, 5.2), hi=2600)
    return x * env(len(x), 0.05, 0.22) * g


def strings(note, sec, hi=1300):
    f = hz(note)
    x = filt(additive(f, sec + 0.4, STR, 0.003, 4.6) + additive(f * 1.003, sec + 0.4, STR, 0.003, 4.1), hi=hi) * 0.5
    return x * env(len(x), 0.25, 0.4)


def flute(note, sec):
    f = hz(note)
    x = additive(f, sec + 0.2, [(1, 1), (2, 0.18), (3, 0.06)], 0.007, 5)
    x = x + filt(noise(sec + 0.2), f * 0.8, f * 3) * 0.08
    return x * env(len(x), 0.07, 0.25)


def bell(f, sec=2.5, damp=1.0):
    n = int(sec * SR)
    t = np.arange(n) / SR
    out = sum(a * np.sin(2 * np.pi * f * r * t) * np.exp(-t / (d * damp)) for r, a, d in ((0.5, 0.5, 2.2), (1, 1, 1.6), (1.19, 0.4, 1.0), (2.0, 0.45, 0.9), (2.76, 0.3, 0.6), (5.4, 0.15, 0.35)))
    return out * env(n, 0.002, 0.05)


def drum(sec=0.8, f0=55, g=1.0):
    n = int(sec * SR)
    t = np.arange(n) / SR
    f = f0 + 60 * np.exp(-t * 18)
    return (np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 4.5) + filt(noise(sec), hi=600) * np.exp(-t * 30) * 0.8) * g


def clink(f, sec=0.5):
    n = int(sec * SR)
    t = np.arange(n) / SR
    out = sum(a * np.sin(2 * np.pi * f * r * t) * np.exp(-t / d) for r, a, d in ((1, 1, 0.12), (2.32, 0.6, 0.07), (4.25, 0.4, 0.04)))
    return out + filt(noise(sec), lo=4000) * np.exp(-t * 120) * 0.4


def reverb(x, sec=1.6, mix=0.25, hi=4500):
    n_ir = int(sec * SR)
    t = np.arange(n_ir) / SR
    ir = filt(rng.standard_normal(n_ir) * np.exp(-6.9 * t / sec), hi=hi)
    ir[:int(0.01 * SR)] = 0
    ir /= np.sqrt(np.sum(ir ** 2)) + 1e-9
    L = len(x) + n_ir
    nfft = 1 << (L - 1).bit_length()
    wet = np.fft.irfft(np.fft.rfft(x, nfft) * np.fft.rfft(ir, nfft), nfft)[:L]
    y = np.concatenate([x, np.zeros(n_ir)]) * (1 - mix) + wet * mix * 1.6
    # buang ekor yang sudah sunyi
    thr = np.max(np.abs(y)) * 0.003
    last = np.nonzero(np.abs(y) > thr)[0]
    return y[:last[-1] + int(0.05 * SR)] if len(last) else y


def save(name, x):
    nf = int(0.03 * SR)
    x[-nf:] *= np.linspace(1, 0, nf)
    x = x / (np.max(np.abs(x)) + 1e-9) * 0.8
    pcm = (np.clip(x, -1, 1) * 32767).astype('<i2').tobytes()
    enc = lameenc.Encoder()
    enc.set_bit_rate(80); enc.set_in_sample_rate(SR); enc.set_channels(1); enc.set_quality(2)
    data = enc.encode(pcm) + enc.flush()
    open(os.path.join(OUT, name + '.mp3'), 'wb').write(data)
    print(name, round(len(x) / SR, 2), 's', len(data), 'bytes')


# wabah: lonceng duka rendah dua kali dan dengung sumbang
x = T(2.6)
place(x, bell(hz('D3'), 2.4, 1.2), 0, 0.8)
place(x, bell(hz('D3'), 2.0, 1.2), 1.0, 0.6)
dr = additive(hz('D2'), 2.6, [(1, 1), (2, 0.3)]) + additive(hz('Eb2'), 2.6, [(1, 0.7)])
place(x, filt(dr, hi=500) * env(int(2.6 * SR), 0.6, 0.8), 0, 0.25)
place(x, filt(noise(2.4), 200, 900) * env(int(2.4 * SR), 0.8, 0.8), 0.1, 0.12)
save('wabah', reverb(x, 2.4, 0.3, 3000))

# kelaparan: suling sendu menurun di atas dengung rendah
x = T(2.4)
for k, (n_, d_) in enumerate((('A4', 0.42), ('G4', 0.42), ('F4', 0.42), ('E4', 0.9))):
    place(x, flute(n_, d_), sum((0.42, 0.42, 0.42)[:k]), 0.7)
place(x, strings('D3', 2.0, 700), 0, 0.35)
save('kelaparan', reverb(x, 2.0, 0.3, 3500))

# rusuh: keramaian marah, besi dipukul, barang pecah
x = T(2.0)
crowd = np.zeros(int(1.9 * SR))
for v in range(9):
    f0 = rng.uniform(250, 700)
    nz = filt(noise(1.9), f0 * 0.8, f0 * 2.2)
    t = np.arange(len(nz)) / SR
    am = 0.5 + 0.5 * np.sin(2 * np.pi * rng.uniform(2.5, 6) * t + rng.uniform(0, 6)) ** 2
    crowd += nz * am
place(x, crowd * env(len(crowd), 0.2, 0.6), 0, 0.5)
place(x, clink(hz('E5'), 0.6), 0.25, 0.5)
place(x, drum(0.5, 70, 0.6), 0.6, 1)
place(x, filt(noise(0.35), 800, 5000) * np.exp(-np.arange(int(0.35 * SR)) / SR * 14), 0.62, 0.7)
place(x, clink(hz('C5'), 0.6), 1.05, 0.4)
save('rusuh', reverb(x, 1.4, 0.2))

# merdeka: seruan terompet menantang (nada sumbang), genderang
x = T(2.2)
place(x, drum(0.9, 50), 0, 0.9)
place(x, horn('D4', 0.35), 0.05, 0.5)
place(x, horn('F4', 0.35), 0.42, 0.5)
place(x, horn('G#4', 1.0), 0.8, 0.55)
place(x, horn('D3', 1.4), 0.8, 0.3)
place(x, drum(0.9, 50), 0.8, 0.7)
save('merdeka', reverb(x, 1.8, 0.28))

# kekaisaran: fanfare agung (D mayor), genderang dan lonceng
x = T(3.6)
fan = [('D4', 0, 0.3), ('D4', 0.32, 0.15), ('D4', 0.5, 0.15), ('A4', 0.68, 0.5), ('F#4', 1.2, 0.3), ('A4', 1.52, 0.3), ('D5', 1.85, 1.4)]
for n_, t_, d_ in fan:
    place(x, horn(n_, d_), t_, 0.45)
    place(x, horn(n_[:-1] + str(int(n_[-1]) - 1), d_), t_, 0.2)
for n_ in ('D3', 'A3', 'F#4'):
    place(x, strings(n_, 1.6, 1800), 1.85, 0.2)
for t_ in (0, 0.68, 1.85):
    place(x, drum(1.0, 48), t_, 0.8)
place(x, bell(hz('D5'), 2.5), 1.85, 0.25)
save('kekaisaran', reverb(x, 2.4, 0.3))

# mundur: terompet tanduk menurun, genderang redup
x = T(2.2)
place(x, horn('D4', 0.4), 0, 0.55)
place(x, horn('A3', 0.4), 0.45, 0.55)
place(x, horn('F3', 1.1), 0.9, 0.55)
place(x, filt(drum(0.8, 45), hi=250), 0, 0.7)
place(x, filt(drum(0.8, 45), hi=250), 0.9, 0.6)
save('mundur', reverb(x, 1.8, 0.3))

# utusan_pergi: derap kuda menjauh dan nada terompet pendek
x = T(1.6)
place(x, horn('A4', 0.25), 0, 0.3)
place(x, horn('D5', 0.35), 0.2, 0.3)
t_ = 0.15
for k in range(10):
    g = 0.9 * (1 - k / 11)
    for dt in (0, 0.075):
        clop = filt(noise(0.06), 300, 2500) * np.exp(-np.arange(int(0.06 * SR)) / SR * 70)
        clop += np.sin(2 * np.pi * 260 * np.arange(int(0.06 * SR)) / SR) * np.exp(-np.arange(int(0.06 * SR)) / SR * 60) * 0.6
        place(x, clop, t_ + dt, g)
    t_ += 0.13
save('utusan_pergi', reverb(x, 1.2, 0.2))

# dagang: koin berdenting jatuh ke kantong, dua petikan riang
x = T(1.6)
t_ = 0
for k in range(9):
    place(x, clink(rng.uniform(2600, 4200), 0.4), t_, rng.uniform(0.3, 0.6))
    t_ += rng.uniform(0.04, 0.09) * (1 + k * 0.08)
place(x, filt(noise(0.2), 100, 900) * np.exp(-np.arange(int(0.2 * SR)) / SR * 20), t_ + 0.02, 0.5)
place(x, flute('A5', 0.2), t_ + 0.1, 0.35)
place(x, flute('D6', 0.45), t_ + 0.28, 0.35)
save('dagang', reverb(x, 1.3, 0.22))

# ditolak: dua nada gesek rendah yang turun, redup
x = T(1.4)
place(x, strings('F3', 0.45, 900), 0, 0.8)
place(x, strings('E3', 0.75, 800), 0.42, 0.8)
place(x, strings('A2', 1.1, 600), 0, 0.4)
place(x, filt(noise(0.3), 1500, 6000) * env(int(0.3 * SR), 0.1, 0.15), 0, 0.08)
save('ditolak', reverb(x, 1.4, 0.25))

# nikah: lonceng pernikahan bersahutan (D mayor) dan gesek hangat
x = T(3.2)
peal = ['D6', 'A5', 'F#5', 'D5', 'A5', 'F#5', 'D6', 'A5', 'D5']
for k, n_ in enumerate(peal):
    place(x, bell(hz(n_), 2.0, 0.8), k * 0.18, 0.35)
for n_ in ('D3', 'A3', 'F#4'):
    place(x, strings(n_, 2.4, 1600), 0.1, 0.18)
save('nikah', reverb(x, 2.2, 0.3))
