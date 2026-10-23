# Asal-usul artefak

`submitted_v1.json` mencatat identitas kandidat yang dikirim: hash arsip, hash setiap member, sumber upstream dan submission ID. `upstream/budget_aware_v10/` berisi empat file referensi untuk memeriksa perubahan. File aktif untuk build selalu berada di `agent/`.

`compiler_wheels.json` mencatat nama, ukuran dan SHA-256 wheel dari dataset resmi penyelenggara. Biner wheel disimpan lokal pada `.local/wheels/` dan tidak dimasukkan ke Git.

Lisensi dan atribusi dipertahankan melalui LICENSE dan NOTICE.txt pada root repo serta salinan aslinya di `agent/`. Salinan di `agent/` merupakan bagian dari identitas ZIP historis; perubahan pada file tersebut akan mengubah hash arsip.
