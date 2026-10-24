# Asal-usul artefak

`submitted_v1.json` mencatat identitas kandidat V1 yang dikirim: hash arsip, hash setiap member, sumber upstream dan submission ID. `agent/` tetap menjadi sumber V1 yang memperoleh skor publik 0.15.

`upstream/budget_aware_v10/` berisi empat file asli versi publik dengan skor 0.22. Reproduksi terpisah memakai folder itu langsung, tanpa perubahan. `reproduction_v10.json` mengikat file dan byte ZIP dengan versi tepat `357955943` serta mencatat hasil submission kita secara terpisah dari hasil upstream. Gunakan `scripts/reproduce_public.py` untuk membangun dan memverifikasi artefak reproduksi.

`compiler_wheels.json` mencatat nama, ukuran dan SHA-256 wheel dari dataset resmi penyelenggara. Biner wheel disimpan lokal pada `.local/wheels/` dan tidak dimasukkan ke Git.

Lisensi dan atribusi dipertahankan melalui LICENSE dan NOTICE.txt pada root repo serta salinan aslinya di `agent/`. Salinan di `agent/` merupakan bagian dari identitas ZIP historis; perubahan pada file tersebut akan mengubah hash arsip.
