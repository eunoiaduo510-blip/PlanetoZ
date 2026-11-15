# PlanetoZ: Daftar Suara

Folder ini berisi semua suara game. Struktur:

```
sound/
  musik/planetoz_base.mp3   backsound base (loop)
  musik/menu.mp3            musik menu utama (loop)
  musik/perang.mp3          musik pertempuran (loop)
  buat_musik.py             pembuat menu.mp3 dan perang.mp3
  sfx/*.mp3                 efek suara (58 file) + suasana amb_*.mp3 (5 file)
  buat_sfx.py               pembuat 11 efek pertempuran & aksi (dirakit dari nada dan derau)
  buat_sfx2.py              pembuat 10 efek kerajaan, diplomasi & dagang
  buat_sfx3.py              pembuat 8 efek musim, kemarau, upgrade, gabung / pisah
  buat_suasana.py           pembuat 5 suara suasana (loop 24 detik)
  DAFTAR_SUARA.md           file ini
```

Nama file = nama yang dipakai di kode lewat `sfx('nama')`.
Contoh: `sfx/perang.mp3` diputar dengan `sfx('perang')`.

---

## A. Sudah ada filenya

### Musik

| File | Durasi | Dipakai untuk |
|---|---|---|
| musik/planetoz_base.mp3 | 3:43 | Backsound base: suling tenang, angin sepoi, kicau burung. Awal dan akhir sangat pelan, aman di-loop. Diputar selama bermain |
| musik/menu.mp3 | 1:09 | Menu utama: kecapi berarpeggio, suling kayu, gesek lembut, lonceng jauh (D dorian, 3/4, 84 bpm). Dibuat dengan `buat_musik.py`, berulang tanpa sambungan |
| musik/perang.mp3 | 0:58 | Pertempuran di peta kota: genderang besar, rebana, petikan dawai, terompet tanduk dan shawm (D minor, 132 bpm). Dibuat dengan `buat_musik.py`, berulang tanpa sambungan |

### Tombol & aksi

| File | Dipakai untuk | Status |
|---|---|---|
| ketuk.mp3 | Ketuk tombol, pilih petak, buka panel | Terpasang |
| taruh.mp3 | Menaruh objek/terrain, sungai, hewan, membangun | Terpasang |
| tolak.mp3 | Aksi tidak bisa dilakukan (iman/bahan kurang, dll) | Terpasang |
| berkah.mp3 | Kuasa berkah, aksi berhasil, janji petisi ditepati | Terpasang |
| koin.mp3 | Mengatur pajak | Terpasang |

### Kota & kerajaan

| File | Dipakai untuk | Status |
|---|---|---|
| kota_baru.mp3 | Kerajaan berdiri, kota pemain berdiri, balai kota naik level | Terpasang |
| bangun.mp3 | Bangunan selesai dibangun/diperbaiki, bangunan naik Lv | Terpasang |
| riset.mp3 | Riset selesai | Terpasang |
| zaman.mp3 | Peradaban memasuki zaman baru, keajaiban selesai | Terpasang |
| takhta.mp3 | Raja baru naik takhta, takhta diperebutkan | Terpasang |
| festival.mp3 | Festival musim, perayaan rakyat, pesta rakyat | Terpasang |
| tamu.mp3 | Rombongan pendatang tiba (kartu pendatang) | Terpasang |
| damai.mp3 | Dua kerajaan bersekutu, perang antar-kerajaan berakhir | Terpasang |

### Perang

| File | Dipakai untuk | Status |
|---|---|---|
| perang.mp3 | Perang dimulai (terompet perang) | Terpasang |
| tempur.mp3 | Musuh tiba dan pertempuran dimulai, serbuan pemain dimulai | Terpasang |
| menang.mp3 | Kota menang bertahan, musuh/monster diusir, kota ditaklukkan atau direbut kembali | Terpasang |
| kalah.mp3 | Balai kota jatuh atau diporak-porandakan, kota direbut musuh | Terpasang |
| tiba.mp3 | Pasukan sampai di tujuan | Terpasang |
| bahaya.mp3 | Bandit/suku menuju wilayah, pemberontakan, perang saudara, pengepungan, monster mendekat | Terpasang |

### Alam & bencana

| File | Dipakai untuk | Status |
|---|---|---|
| hujan.mp3 | Kuasa hujan berkah, hujan badai mendekati kota | Terpasang |
| petir.mp3 | Kuasa petir dan badai hujan | Terpasang |
| taufan.mp3 | Kuasa taufan, taufan mendekati kota | Terpasang |
| banjir.mp3 | Banjir (kuasa dan survival) | Terpasang |
| belalang.mp3 | Kawanan belalang muncul | Terpasang |
| api.mp3 | Kuasa api, kebakaran hutan, api merambat ke bangunan | Terpasang |
| gempa.mp3 | Gempa bumi, bangunan musuh hancur | Terpasang |
| meteor.mp3 | Meteor jatuh | Terpasang |
| ledak.mp3 | Ledakan, letusan gunung berapi | Terpasang |

### Akhir

| File | Dipakai untuk | Status |
|---|---|---|
| gameover.mp3 | Game over: semua jiwa suku habis | Terpasang |

### Pertempuran & aksi (dibuat dengan `buat_sfx.py`)

| File | Dipakai untuk | Status |
|---|---|---|
| pedang.mp3 | Pedang beradu saat pertempuran di peta kota (serangan jarak dekat) | Terpasang |
| panah.mp3 | Panah dilepas (pemanah, menara) | Terpasang |
| gugur.mp3 | Prajurit / musuh tumbang | Terpasang |
| dobrak.mp3 | Gerbang, tembok, atau menara dipukul | Terpasang |
| runtuh.mp3 | Tembok / bangunan runtuh dalam pertempuran | Terpasang |
| berangkat.mp3 | Terompet tanduk: pasukan berangkat, menyerbu, atau pulang | Terpasang |
| latih.mp3 | Regu baru selesai dilatih | Terpasang |
| bongkar.mp3 | Bangunan atau rumah penduduk dibongkar | Terpasang |
| padam.mp3 | Api berhasil dipadamkan warga | Terpasang |
| jelajah.mp3 | Penjelajah kembali, daerah baru terlihat | Terpasang |
| bijih.mp3 | Penambang menemukan bijih besi | Terpasang |

Suara pertempuran memakai jeda pendek (pedang 0,16 detik, panah 0,14, gugur 0,25, dobrak 0,6, runtuh 0,8) dan volume lebih pelan karena sering berbunyi.

### Kerajaan, diplomasi & dagang (dibuat dengan `buat_sfx2.py`)

| File | Dipakai untuk | Status |
|---|---|---|
| wabah.mp3 | Wabah menjangkiti rakyatmu (juga kuasa Wabah di creative) | Terpasang |
| kelaparan.mp3 | Stok makanan baru saja habis | Terpasang |
| rusuh.mp3 | Mogok kerja, perusuh membakar bangunan, penjarahan | Terpasang |
| merdeka.mp3 | Kotamu memberontak, bawahan melepaskan diri, kerajaan merdeka | Terpasang |
| kekaisaran.mp3 | Kerajaan naik jadi kekaisaran / raja bergelar Maharaja | Terpasang |
| mundur.mp3 | Pasukanmu mundur dari serbuan (serbuan gagal total memakai `kalah`) | Terpasang |
| utusan_pergi.mp3 | Utusanmu atau utusan dagangmu berangkat | Terpasang |
| dagang.mp3 | Perjanjian dagang disetujui | Terpasang |
| ditolak.mp3 | Utusanmu kembali membawa penolakan | Terpasang |
| nikah.mp3 | Pernikahan wangsa diterima | Terpasang |

### Musim & aksi kecil (dibuat dengan `buat_sfx3.py`)

| File | Dipakai untuk | Status |
|---|---|---|
| musim_semi.mp3 | Musim berganti ke semi: petikan riang dan kicau burung | Terpasang |
| musim_panas.mp3 | Musim berganti ke panas: suling hangat dan tonggeret | Terpasang |
| musim_gugur.mp3 | Musim berganti ke gugur: petikan sendu dan daun berdesir | Terpasang |
| musim_dingin.mp3 | Musim berganti ke dingin: lonceng kristal dan angin dingin | Terpasang |
| kemarau.mp3 | Kemarau panjang mulai | Terpasang |
| upgrade.mp3 | Upgrade bangunan atau balai kota dimulai | Terpasang |
| gabung.mp3 | Regu digabung | Terpasang |
| pisah.mp3 | Satu regu dipisah jadi pasukan baru | Terpasang |

### Suasana (loop pelan, dibuat dengan `buat_suasana.py`)

| File | Menyala saat | Status |
|---|---|---|
| amb_hujan.mp3 | Hujan di tempat yang sedang dilihat (planet atau kota) | Terpasang |
| amb_ombak.mp3 | (Dimatikan: terlalu berisik. Filenya disimpan; untuk menyalakan lagi, tambahkan `ombak` ke `AMB` dan kondisinya di `ambWant`) | Tidak dipakai |
| amb_malam.mp3 | Malam hari (jam 18.00–06.00), jangkrik dan burung hantu; tidak di musim dingin | Terpasang |
| amb_angin.mp3 | Musim dingin | Terpasang |
| amb_kota.mp3 | Siang hari di peta wilayah: gumam warga, palu pandai besi, kapak, langkah | Terpasang |

Suasana muncul dan hilang pelan (sekitar 2 detik), lebih pelan di tampilan planet, tidak ada di menu utama. Tiap suasana diputar bergantian dua salinan dengan silang-pudar 1,2 detik supaya tidak ada jeda di ujung file. Volume di `AMB` dan `AMB_VOL` (index.html).

"Terpasang" = game memutar file ini langsung dari folder `sound/` (tidak disalin ke index.html).

---

## B. Belum ada suaranya (belum dibuat)

### Kejadian yang tampil sebagai pesan tapi masih tanpa suara

- Desa / kota baru berdiri (pemukiman AI)
- Kerajaan menemukan teknologi, teknologi menyebar
- Pemenang perebutan takhta, raja baru memutus persekutuan
- Kemarau panjang berakhir
- Hewan liar punah dari planet
- Suku lain punah, suku baru muncul
- Wilayah kini milikmu
- Penjelajah berangkat
- Belalang melahap ladang
- Taufan merusak bangunan di kota
- Serbuan pemain gagal / mundur
- Waktu dijeda / dilanjutkan, ganti kecepatan

### Musik lain

- Musik malam
- Musik game over (lebih panjang dari sfx gameover)

---

## Cara kerja di game

- `index.html` memutar suara langsung dari folder ini: `sound/sfx/<nama>.mp3` dan `sound/musik/planetoz_base.mp3`. **Folder `sound` harus tetap di sebelah `index.html`** (juga saat diunggah atau dibagikan). Jalan juga saat game dibuka langsung dari file (klik dua kali).
- **Mengganti suara**: timpa file dengan nama yang sama, lalu muat ulang game. Tidak perlu mengubah kode.
- **Membuat ulang / mengubah efek buatan**: ubah resepnya di `buat_sfx.py` atau `buat_sfx2.py`, lalu jalankan `python sound/buat_sfx.py sound/sfx` (butuh `pip install lameenc`) atau `python sound/buat_sfx2.py sound/sfx` / `python sound/buat_sfx3.py sound/sfx` (butuh `pip install numpy lameenc`). Hasilnya menimpa file dengan nama yang sama.
- **Volume** tiap efek diatur di `SFX_VOL` (index.html) supaya kekerasannya seimbang; volume keseluruhan `SFX_MASTER` (0,7) dan musik `BGM_VOL` (0,28). Bila mengganti file dengan yang jauh lebih keras / pelan, sesuaikan angkanya.
- **Jeda minimum**: suara kejadian yang sama tidak diputar lagi dalam 1,5 detik (ketuk / taruh / tolak / koin hampir tanpa jeda), supaya kejadian beruntun tidak menumpuk.
- **Musik latar** berganti otomatis dengan peralihan halus (1,6 detik): menu utama = `menu.mp3`, bermain = `planetoz_base.mp3`, pertempuran di peta kota = `perang.mp3` (selalu dari awal, kembali ke base setelah pertempuran usai). Mulai setelah layar pertama kali disentuh (aturan browser), ikut tombol suara, berhenti saat tab disembunyikan. Volume tiap lagu di `MUSIC` (index.html).
- **Membuat ulang musik**: ubah not / alat musik di `buat_musik.py`, lalu jalankan `python sound/buat_musik.py sound/musik` (butuh `pip install numpy lameenc`, sekitar 45 detik).
- Bila sebuah file hilang atau gagal dimuat, game memakai bip sintetis lama (untuk 9 suara lama) atau diam, tanpa error.
- Suara kartu kunjungan: pendatang, pengungsi, pedagang, ahli, tentara bayaran, orang asing, dan utusan = `tamu`; musuh mendekat dan pengepungan = `bahaya`; pasukan tiba di kota musuh = `tempur`; pilih budaya = `zaman`; petisi = `ketuk`.
