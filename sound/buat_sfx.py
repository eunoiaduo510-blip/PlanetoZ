# Pembuat efek suara PlanetoZ: semua dirakit dari nada dan derau (tanpa rekaman), lalu disimpan sebagai mp3.
import math, random, struct, sys, os
import lameenc

SR = 44100
OUT = sys.argv[1] if len(sys.argv) > 1 else 'out'
os.makedirs(OUT, exist_ok=True)
TAU = 2 * math.pi


def buf(sec):
    return [0.0] * int(SR * sec)


def add(dst, src, at=0.0, gain=1.0):
    o = int(at * SR)
    for i, v in enumerate(src):
        j = o + i
        if j >= len(dst):
            break
        dst[j] += v * gain


def env(n, a, d, curve=4.0):
    """serangan a detik lalu meluruh eksponensial selama d detik"""
    out = []
    na = max(1, int(a * SR))
    for i in range(n):
        t = i / SR
        if i < na:
            out.append(i / na)
        else:
            out.append(math.exp(-curve * (t - a) / max(d, 1e-4)))
    return out


def tone(sec, f0, f1=None, wave='sine', a=0.005, d=None, vib=0.0, vibf=5.0, harm=None):
    n = int(sec * SR)
    f1 = f0 if f1 is None else f1
    e = env(n, a, d if d else sec)
    ph = 0.0
    out = []
    for i in range(n):
        t = i / n
        f = f0 * (f1 / f0) ** t
        if vib:
            f *= 1 + vib * math.sin(TAU * vibf * i / SR)
        ph += TAU * f / SR
        if harm:
            v = sum(h[1] * math.sin(ph * h[0]) for h in harm)
        elif wave == 'sine':
            v = math.sin(ph)
        elif wave == 'tri':
            v = 2 / math.pi * math.asin(math.sin(ph))
        elif wave == 'saw':
            v = ((ph / TAU) % 1) * 2 - 1
        else:
            v = 1.0 if math.sin(ph) > 0 else -1.0
        out.append(v * e[i])
    return out


def noise(sec, a=0.002, d=None, lp=None, hp=None, curve=4.0):
    n = int(sec * SR)
    e = env(n, a, d if d else sec, curve)
    out = []
    y = 0.0
    z = 0.0
    px = 0.0
    al = 1 - math.exp(-TAU * lp / SR) if lp else 1.0
    ah = math.exp(-TAU * hp / SR) if hp else 0.0
    for i in range(n):
        x = random.uniform(-1, 1)
        y += al * (x - y)            # lowpass
        if hp:
            z = ah * (z + y - px)    # highpass
            px = y
            v = z
        else:
            v = y
        out.append(v * e[i])
    return out


def bandnoise(sec, f0, f1, q=6.0, a=0.005, d=None, curve=4.0):
    """derau bandpass (resonator 2-kutub) dengan frekuensi tengah bergeser"""
    n = int(sec * SR)
    e = env(n, a, d if d else sec, curve)
    y1 = y2 = 0.0
    out = []
    for i in range(n):
        t = i / n
        f = f0 * (f1 / f0) ** t
        r = 1 - math.pi * f / (q * SR)
        c = 2 * r * math.cos(TAU * f / SR)
        x = random.uniform(-1, 1) * (1 - r)
        y = x + c * y1 - r * r * y2
        y2, y1 = y1, y
        out.append(y * e[i] * 4)
    return out


def metal(sec, base, ratios=(1, 1.48, 2.11, 2.73, 3.62, 4.37), d=0.35, bright=1.0):
    n = int(sec * SR)
    out = [0.0] * n
    for k, rt in enumerate(ratios):
        f = base * rt * random.uniform(0.995, 1.005)
        dd = d / (1 + 0.35 * k)
        amp = (0.8 ** k) * (bright if k > 2 else 1)
        for i in range(n):
            out[i] += amp * math.sin(TAU * f * i / SR) * math.exp(-i / SR / dd)
    return out


def pluck(sec, f, damp=0.996):
    n = int(sec * SR)
    p = max(2, int(SR / f))
    line = [random.uniform(-1, 1) for _ in range(p)]
    out = []
    for i in range(n):
        v = line[i % p]
        nxt = line[(i + 1) % p]
        line[i % p] = damp * 0.5 * (v + nxt)
        out.append(v)
    return out


def reverb(x, mix=0.25, room=0.5):
    """reverb sederhana: beberapa comb paralel + allpass"""
    n = len(x)
    out = [0.0] * n
    for dl, fb in ((1557, 0.77), (1617, 0.76), (1491, 0.78), (1422, 0.79), (1277, 0.8), (1356, 0.79)):
        dl = int(dl * (0.6 + room))
        fb *= 0.92 + 0.08 * room
        b = [0.0] * dl
        k = 0
        lp = 0.0
        for i in range(n):
            y = b[k]
            lp = lp * 0.3 + y * 0.7
            b[k] = x[i] + lp * fb
            k = (k + 1) % dl
            out[i] += y / 6
    for dl, g in ((225, 0.5), (556, 0.5)):
        b = [0.0] * dl
        k = 0
        for i in range(n):
            bv = b[k]
            y = -g * out[i] + bv
            b[k] = out[i] + g * y
            k = (k + 1) % dl
            out[i] = y
    return [x[i] * (1 - mix) + out[i] * mix * 2.2 for i in range(n)]


def finish(x, peak=0.8, fade=0.02):
    n = len(x)
    nf = int(fade * SR)
    for i in range(nf):
        x[n - 1 - i] *= i / nf
    m = max(1e-6, max(abs(v) for v in x))
    return [v / m * peak for v in x]


def save(name, x):
    x = finish(x)
    pcm = b''.join(struct.pack('<h', int(max(-1, min(1, v)) * 32767)) for v in x)
    enc = lameenc.Encoder()
    enc.set_bit_rate(80)
    enc.set_in_sample_rate(SR)
    enc.set_channels(1)
    enc.set_quality(2)
    data = enc.encode(pcm) + enc.flush()
    open(os.path.join(OUT, name + '.mp3'), 'wb').write(data)
    print(name, round(len(x) / SR, 2), 's', len(data), 'bytes')


random.seed(87)

# pedang: dua bilah besi beradu, dentang singkat berdenging
x = buf(0.75)
add(x, noise(0.05, d=0.03, hp=2500), 0, 0.9)
add(x, metal(0.75, 1650, d=0.32, bright=0.8), 0, 0.5)
add(x, metal(0.6, 2380, d=0.18), 0.012, 0.25)
save('pedang', reverb(x, 0.18, 0.3))

# panah: desing tali busur lalu anak panah melesat dan menancap
x = buf(0.6)
add(x, tone(0.08, 210, 150, 'tri', d=0.07), 0, 0.5)
add(x, bandnoise(0.38, 900, 3800, q=4, a=0.03, d=0.5, curve=2), 0.02, 0.9)
add(x, noise(0.05, d=0.04, lp=900), 0.42, 0.7)
add(x, tone(0.12, 160, 90, d=0.1), 0.42, 0.6)
save('panah', reverb(x, 0.12, 0.2))

# gugur: tubuh berzirah jatuh ke tanah
x = buf(0.9)
add(x, noise(0.4, d=0.18, lp=260), 0, 1.0)
add(x, tone(0.35, 95, 48, d=0.25), 0, 0.8)
add(x, metal(0.4, 980, d=0.12), 0.03, 0.18)
add(x, noise(0.08, d=0.05, hp=1800), 0.05, 0.25)
add(x, noise(0.3, d=0.12, lp=220), 0.22, 0.45)
save('gugur', reverb(x, 0.2, 0.35))

# dobrak: pendobrak menghantam gerbang kayu
x = buf(1.3)
add(x, tone(0.7, 78, 38, d=0.45), 0, 1.0)
add(x, noise(0.5, d=0.25, lp=420), 0, 0.9)
add(x, bandnoise(0.12, 1400, 900, q=3, d=0.08), 0.005, 0.6)
add(x, noise(0.25, d=0.1, lp=1500, hp=500), 0.04, 0.35)
save('dobrak', reverb(x, 0.3, 0.6))

# runtuh: tembok / bangunan ambruk, batu berjatuhan
x = buf(2.2)
add(x, noise(2.0, a=0.05, d=1.4, lp=180, curve=3), 0, 0.9)
add(x, tone(1.2, 60, 32, d=0.9), 0, 0.7)
for k in range(16):
    t = 0.05 + random.random() ** 1.6 * 1.5
    add(x, noise(0.12, d=0.05, lp=random.uniform(600, 2200)), t, random.uniform(0.2, 0.55) * (1 - t / 2))
    if random.random() < 0.5:
        add(x, tone(0.15, random.uniform(110, 190), 70, d=0.08), t, 0.35)
save('runtuh', reverb(x, 0.3, 0.7))

# berangkat: tiup terompet tanduk, dua nada naik
H = [(1, 1), (2, 0.55), (3, 0.35), (4, 0.2), (5, 0.12), (6, 0.06)]
x = buf(1.9)
add(x, tone(0.5, 196, harm=H, a=0.06, d=1.5, vib=0.004), 0, 0.5)
add(x, tone(1.25, 294, harm=H, a=0.07, d=2.2, vib=0.006, vibf=5.5), 0.48, 0.55)
add(x, noise(0.4, a=0.05, d=0.3, lp=1200, hp=400), 0, 0.04)
save('berangkat', reverb(x, 0.3, 0.6))

# latih: tiga hentakan genderang, lalu tombak dihentak bersamaan
x = buf(1.3)
for k, t in enumerate((0, 0.2, 0.4)):
    add(x, tone(0.3, 120, 70, d=0.18), t, 0.8)
    add(x, noise(0.12, d=0.06, lp=1800, hp=200), t, 0.35)
add(x, noise(0.08, d=0.05, lp=700), 0.68, 0.9)
add(x, tone(0.25, 90, 55, d=0.15), 0.68, 0.7)
add(x, metal(0.55, 1320, d=0.2), 0.69, 0.25)
save('latih', reverb(x, 0.22, 0.45))

# bongkar: kayu dicungkil dan berderak patah
x = buf(1.2)
for k in range(9):
    t = 0.02 + k * 0.045 + random.uniform(0, 0.02)
    add(x, bandnoise(0.05, random.uniform(700, 1600), 600, q=5, d=0.03), t, random.uniform(0.4, 0.8))
add(x, noise(0.3, d=0.15, lp=1300, hp=250), 0.42, 0.7)
add(x, tone(0.3, 110, 60, d=0.2), 0.62, 0.7)
add(x, noise(0.3, d=0.15, lp=300), 0.62, 0.6)
save('bongkar', reverb(x, 0.2, 0.4))

# padam: air disiram, api mendesis lalu hilang
x = buf(1.5)
add(x, noise(0.25, d=0.2, lp=900, hp=150), 0, 0.6)
hiss = noise(1.4, a=0.03, d=1.0, hp=3000, curve=3)
for i in range(len(hiss)):
    hiss[i] *= 0.6 + 0.4 * math.sin(TAU * 13 * i / SR + math.sin(TAU * 3 * i / SR))
add(x, hiss, 0.05, 0.8)
add(x, bandnoise(0.5, 2600, 1400, q=3, a=0.05, d=0.4), 0.05, 0.25)
save('padam', reverb(x, 0.15, 0.3))

# jelajah: petikan lembut naik (daerah baru terlihat)
x = buf(1.9)
for k, f in enumerate((392, 440, 523.25, 659.25, 783.99)):
    p = pluck(1.4, f, 0.9965)
    add(x, p, k * 0.11, 0.55)
add(x, tone(1.2, 1568, harm=[(1, 0.5), (2, 0.2)], a=0.2, d=1.0), 0.45, 0.12)
save('jelajah', reverb(x, 0.35, 0.6))

# bijih: beliung menghantam batu dua kali, lalu kilau kecil
x = buf(1.2)
for t in (0, 0.22):
    add(x, noise(0.05, d=0.03, lp=3000, hp=800), t, 0.7)
    add(x, metal(0.4, 1900, d=0.12), t, 0.35)
    add(x, tone(0.12, 220, 140, d=0.06), t, 0.4)
for k, f in enumerate((1318.5, 1760, 2093)):
    add(x, tone(0.6, f, a=0.005, d=0.35), 0.48 + k * 0.07, 0.22)
save('bijih', reverb(x, 0.3, 0.5))
