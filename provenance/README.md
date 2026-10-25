# Asal-usul artefak

`combined_v2.json` mencatat kandidat utama di `agent/`: gabungan temperature 0, enam tool, dan instruksi pemulihan error berulang. Manifest mengikat sumber dengan hash ZIP dan memisahkan validasi compiler dari skor kualitas.

`submitted_v1.json` mencatat identitas historis V1 yang memperoleh skor publik 0.15. Field `source_git_commit` menunjuk revisi repo yang masih berisi enam file sumber V1. Checkout revisi tersebut di lokasi lain untuk membangun ulang artefak V1; `agent/` saat ini berisi Combined V2.

`upstream/budget_aware_v10/` berisi empat file asli versi publik dengan skor 0.22. Reproduksi terpisah memakai folder itu langsung, tanpa perubahan. `reproduction_v10.json` mengikat file dan byte ZIP dengan versi tepat `357955943` serta mencatat hasil submission kita secara terpisah dari hasil upstream. Gunakan `scripts/reproduce_public.py` untuk membangun dan memverifikasi artefak reproduksi.

`compiler_wheels.json` mencatat nama, ukuran dan SHA-256 wheel dari dataset resmi penyelenggara. Biner wheel disimpan lokal pada `.local/wheels/` dan tidak dimasukkan ke Git.

Lisensi dan atribusi dipertahankan melalui LICENSE dan NOTICE.txt pada root repo serta berkas dalam `agent/`. NOTICE dalam `agent/` menjelaskan perubahan Combined V2 dan merupakan bagian dari hash ZIP kandidat saat ini.
