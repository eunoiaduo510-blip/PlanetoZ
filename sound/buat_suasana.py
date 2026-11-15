# Pembuat suara suasana PlanetoZ (loop pelan): hujan, ombak, jangkrik malam, angin musim dingin, keramaian kota.
# Pemakaian: python buat_suasana.py <folder_keluar>   (butuh: pip install numpy lameenc; memakai alat dari buat_sfx2.py di folder yang sama)
import sys, os
sys.argv = [sys.argv[0], sys.argv[1] if len(sys.argv) > 1 else 'out']
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, 'buat_sfx2.py' if os.path.exists(os.path.join(HERE, 'buat_sfx2.py')) else 'gen_sfx2.py'), encoding='utf-8').read()
exec(src.split('# wabah:')[0])
import lameenc
rng = np.random.default_rng(91)
L = 24.0   # panjang loop (detik)
X = 2.0    # silang-pudar di sambungan


def loop(x):
    n, nx = int(L * SR), int(X * SR)
    y = x[:n].copy()
    w = np.linspace(0, 1, nx)
    y[:nx] = x[:nx] * np.sqrt(w) + x[n:n + nx] * np.sqrt(1 - w)
    return y


def slow(sec, rate, lo=0.0, hi=1.0, seed=0):
    """kurva acak halus (untuk embusan / gelombang)"""
    r = np.random.default_rng(seed)
    pts = int(sec * rate) + 4
    k = r.uniform(lo, hi, pts)
    xs = np.linspace(0, sec, pts)
    t = np.arange(int(sec * SR)) / SR
    return np.interp(t, xs, k)


def save_amb(name, x, kbps=64):
    x = x - np.mean(x)
    x = x / (np.max(np.abs(x)) + 1e-9) * 0.8
    pcm = (np.clip(x, -1, 1) * 32767).astype('<i2').tobytes()
    enc = lameenc.Encoder()
    enc.set_bit_rate(kbps); enc.set_in_sample_rate(SR); enc.set_channels(1); enc.set_quality(2)
    data = enc.encode(pcm) + enc.flush()
    open(os.path.join(OUT, name + '.mp3'), 'wb').write(data)
    print(name, round(len(x) / SR, 1), 's', len(data) // 1024, 'KB')


D = L + X + 0.5
N = int(D * SR)
t = np.arange(N) / SR

# ---------- hujan: desir rapat, tetes acak, gemuruh jauh ----------
x = filt(noise(D), 700, 7000) * (0.75 + 0.25 * slow(D, 0.5, seed=1))
drops = np.zeros(N)
for k in range(int(D * 55)):
    i = rng.integers(0, N - 2000)
    n = rng.integers(200, 900)
    f = rng.uniform(1500, 6000)
    tt = np.arange(n) / SR
    drops[i:i + n] += np.sin(2 * np.pi * f * tt) * np.exp(-tt * rng.uniform(150, 400)) * rng.uniform(0.2, 1)
x += drops * 0.35
x += filt(noise(D), 30, 160) * 0.6 * slow(D, 0.3, 0.3, 1, seed=2)
save_amb('amb_hujan', loop(x))

# ---------- ombak: gelombang datang dan surut ----------
wave = np.zeros(N)
tpos = 0.0
while tpos < D:
    per = rng.uniform(5.0, 7.5)
    n = int(per * SR)
    tt = np.arange(n) / SR
    shape = np.clip(np.sin(np.pi * tt / per) ** 1.5, 0, 1) * np.exp(-((tt / per - 0.45) ** 2) * 3)
    crest = np.exp(-((tt / per - 0.42) ** 2) * 60)
    seg = filt(noise(per), 80, 900) * shape + filt(noise(per), 1500, 6000) * crest * 0.35 + filt(noise(per), 600, 3000) * shape * 0.25
    i = int(tpos * SR)
    m = min(n, N - i)
    wave[i:i + m] += seg[:m] * rng.uniform(0.7, 1.0)
    tpos += per * rng.uniform(0.55, 0.75)
wave += filt(noise(D), 60, 300) * 0.15
save_amb('amb_ombak', loop(wave))

# ---------- malam: jangkrik dan burung hantu sesekali ----------
x = filt(noise(D), 200, 2000) * 0.03
for c in range(4):
    f = rng.uniform(4200, 5200)
    rate = rng.uniform(0.45, 0.8)
    pulses = rng.integers(3, 5)
    tc = rng.uniform(0, 0.5)
    g = rng.uniform(0.25, 0.6)
    while tc < D - 0.3:
        for p in range(pulses):
            n = int(0.018 * SR)
            tt = np.arange(n) / SR
            ch = np.sin(2 * np.pi * f * tt) * np.sin(np.pi * tt / 0.018) ** 2
            i = int((tc + p * 0.034) * SR)
            x[i:i + n] += ch * g
        tc += rate * rng.uniform(0.9, 1.1)
for t0 in (6.0, 17.5):   # burung hantu: hu ... hu-hu
    for k, (dt, d) in enumerate(((0, 0.45), (0.75, 0.22), (1.0, 0.5))):
        n = int(d * SR)
        tt = np.arange(n) / SR
        f = 390 * (1 - 0.06 * tt / d)
        hoot = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * tt / d) ** 1.5
        place(x, hoot, t0 + dt, 0.35)
save_amb('amb_malam', loop(x))

# ---------- angin musim dingin: embusan dan siulan ----------
x = np.zeros(N)
for k, fc in enumerate((260, 520, 900, 1500)):
    band = filt(noise(D), fc * 0.6, fc * 1.5)
    x += band * slow(D, 0.35 + 0.1 * k, 0.1, 1, seed=10 + k) * (1.0 / (1 + k * 0.4))
wh = slow(D, 0.25, 600, 1100, seed=20)
x += np.sin(2 * np.pi * np.cumsum(wh) / SR) * slow(D, 0.3, 0, 1, seed=21) ** 3 * 0.06
save_amb('amb_angin', loop(x))

# ---------- kota: gumam warga, palu pandai besi, kapak, langkah ----------
x = np.zeros(N)
for v in range(12):
    f0 = rng.uniform(220, 650)
    nz = filt(noise(D), f0 * 0.8, f0 * 2.0)
    am = np.clip(np.sin(2 * np.pi * rng.uniform(1.5, 4) * t + rng.uniform(0, 6)), 0, 1) ** 2 * slow(D, 0.4, 0.2, 1, seed=30 + v)
    x += nz * am * 0.25
tc = 1.0
while tc < D - 1:   # palu: 3-5 ketukan
    for k in range(rng.integers(3, 6)):
        n = int(0.25 * SR); tt = np.arange(n) / SR
        hit = sum(a * np.sin(2 * np.pi * f * tt) * np.exp(-tt / d) for f, a, d in ((1350, 1, 0.08), (3100, 0.5, 0.04)))
        place(x, hit, tc + k * 0.42, 0.18)
    tc += rng.uniform(4, 7)
tc = 3.0
while tc < D - 1:   # kapak membelah kayu
    for k in range(rng.integers(2, 4)):
        n = int(0.15 * SR); tt = np.arange(n) / SR
        chop = filt(noise(0.15), 300, 2500) * np.exp(-tt * 40) + np.sin(2 * np.pi * 180 * tt) * np.exp(-tt * 35) * 0.6
        place(x, chop, tc + k * 0.9, 0.22)
    tc += rng.uniform(6, 9)
for k in range(int(D * 1.2)):   # langkah
    n = int(0.08 * SR); tt = np.arange(n) / SR
    place(x, filt(noise(0.08), 150, 1200) * np.exp(-tt * 50), rng.uniform(0, D - 0.2), 0.06)
save_amb('amb_kota', loop(x))
