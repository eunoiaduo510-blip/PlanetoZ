# Pembuat efek suara PlanetoZ bagian 3 (musim, kemarau, upgrade, gabung / pisah regu): dirakit dari nada dan derau, disimpan mp3.
# Pemakaian: python buat_sfx3.py <folder_keluar>   (butuh: pip install numpy lameenc; memakai alat dari buat_sfx2.py di folder yang sama)
import sys, os
sys.argv = [sys.argv[0], sys.argv[1] if len(sys.argv) > 1 else 'out']
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, 'buat_sfx2.py' if os.path.exists(os.path.join(HERE, 'buat_sfx2.py')) else 'gen_sfx2.py'), encoding='utf-8').read()
exec(src.split('# wabah:')[0])   # ambil alat-alatnya saja (hz, place, horn, flute, bell, reverb, save, ...)
rng = np.random.default_rng(90)


def pluck(f, sec, damp=0.995, bright=0.5):
    n = int(sec * SR)
    p = max(2, int(round(SR / f)))
    buf = rng.uniform(-1, 1, p)
    buf = bright * buf + (1 - bright) * np.convolve(buf, np.ones(4) / 4, 'same')
    out = np.zeros(n)
    i = 0
    while i < n:
        m = min(p, n - i)
        out[i:i + m] = buf[:m]
        buf = damp * 0.5 * (buf + np.roll(buf, -1))
        i += p
    return out * env(n, 0.002, 0.08)


def birds(sec, count=4):
    x = T(sec)
    for k in range(count):
        t0 = rng.uniform(0.1, sec - 0.5)
        for c in range(rng.integers(2, 4)):
            d = rng.uniform(0.05, 0.09)
            n = int(d * SR)
            t = np.arange(n) / SR
            f = rng.uniform(2800, 4200) * (1 + 0.35 * np.sin(np.pi * t / d))
            ch = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * t / d) ** 2
            place(x, ch, t0 + c * rng.uniform(0.08, 0.13), 0.25)
    return x


# musim semi: petikan riang naik + kicau burung
x = T(2.4)
for k, n_ in enumerate(('D5', 'E5', 'F#5', 'A5', 'D6')):
    place(x, pluck(hz(n_), 1.6, 0.996), k * 0.1, 0.45)
place(x, birds(2.3, 4), 0, 0.8)
save('musim_semi', reverb(x, 1.6, 0.25))

# musim panas: suling hangat dan dengung jangkrik / tonggeret
x = T(2.6)
place(x, flute('A4', 0.5), 0, 0.5)
place(x, flute('D5', 0.5), 0.45, 0.5)
place(x, flute('C#5', 0.9), 0.9, 0.5)
n = int(2.4 * SR); t = np.arange(n) / SR
cic = filt(noise(2.4), 4500, 7500) * (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 28 * t))) * env(n, 0.5, 0.8)
place(x, cic, 0.1, 0.12)
save('musim_panas', reverb(x, 1.6, 0.25))

# musim gugur: petikan sendu menurun dan angin daun berdesir
x = T(2.6)
for k, n_ in enumerate(('A4', 'G4', 'F4', 'D4')):
    place(x, pluck(hz(n_), 1.8, 0.996, 0.4), k * 0.28, 0.5)
n = int(2.4 * SR); t = np.arange(n) / SR
leaves = filt(noise(2.4), 1500, 6000) * (0.4 + 0.6 * np.abs(np.sin(2 * np.pi * 1.3 * t))) * env(n, 0.6, 0.9)
place(x, leaves, 0.05, 0.18)
save('musim_gugur', reverb(x, 1.8, 0.28))

# musim dingin: lonceng kristal pelan dan angin dingin
x = T(3.0)
for k, n_ in enumerate(('D6', 'A5', 'F5', 'D5')):
    place(x, bell(hz(n_), 2.0, 0.7), k * 0.32, 0.25)
n = int(2.8 * SR); t = np.arange(n) / SR
wind = np.zeros(n)
for k in range(3):
    fc = 500 + 300 * k
    wind += filt(noise(2.8), fc * 0.7, fc * 1.4) * (0.5 + 0.5 * np.sin(2 * np.pi * (0.4 + 0.15 * k) * t + k))
place(x, wind * env(n, 0.8, 1.0), 0, 0.2)
save('musim_dingin', reverb(x, 2.4, 0.3))

# kemarau: dengung panas yang bergetar, tanah retak
x = T(2.4)
n = int(2.3 * SR); t = np.arange(n) / SR
drone = additive(hz('A2'), 2.3, [(1, 1), (2, 0.4), (3, 0.2)], 0.012, 3.0) * env(n, 0.5, 0.8)
place(x, filt(drone, hi=900), 0, 0.5)
place(x, filt(noise(2.3), 300, 1200) * env(n, 0.7, 0.8) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.7 * t)), 0, 0.15)
for k in range(5):
    t0 = 0.6 + k * 0.22 + rng.uniform(0, 0.08)
    place(x, filt(noise(0.04), 1500, 6000) * np.exp(-np.arange(int(0.04 * SR)) / SR * 90), t0, 0.5)
save('kemarau', reverb(x, 1.6, 0.22))

# upgrade: palu dua kali lalu kilau naik
x = T(1.6)
for t0 in (0, 0.18):
    n = int(0.3 * SR); tt = np.arange(n) / SR
    hit = sum(a * np.sin(2 * np.pi * f * tt) * np.exp(-tt / d) for f, a, d in ((1180, 1, 0.09), (2730, 0.5, 0.05), (4100, 0.3, 0.03)))
    hit += filt(noise(0.3), 1000, 6000) * np.exp(-tt * 80) * 0.6
    place(x, hit, t0, 0.5)
for k, n_ in enumerate(('A5', 'D6', 'F#6')):
    place(x, bell(hz(n_), 1.2, 0.5), 0.42 + k * 0.08, 0.18)
save('upgrade', reverb(x, 1.3, 0.22))

# gabung: langkah berbaris bersatu dan dua nada naik terompet
x = T(1.4)
for k in range(4):
    n = int(0.12 * SR); tt = np.arange(n) / SR
    step = filt(noise(0.12), 150, 1500) * np.exp(-tt * 35) + np.sin(2 * np.pi * 110 * tt) * np.exp(-tt * 30) * 0.5
    place(x, step, k * 0.14, 0.5 + k * 0.1)
place(x, horn('A3', 0.25), 0.55, 0.35)
place(x, horn('D4', 0.55), 0.78, 0.4)
save('gabung', reverb(x, 1.3, 0.22))

# pisah: dua nada turun terompet dan langkah memisah
x = T(1.4)
place(x, horn('D4', 0.25), 0, 0.35)
place(x, horn('A3', 0.5), 0.24, 0.35)
for k in range(3):
    n = int(0.12 * SR); tt = np.arange(n) / SR
    step = filt(noise(0.12), 150, 1500) * np.exp(-tt * 35) + np.sin(2 * np.pi * 110 * tt) * np.exp(-tt * 30) * 0.5
    place(x, step, 0.75 + k * 0.16, 0.7 - k * 0.15)
save('pisah', reverb(x, 1.3, 0.22))
