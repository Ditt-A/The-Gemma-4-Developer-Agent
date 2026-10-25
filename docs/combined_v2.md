# Budget-Aware Combined V2

Satu kandidat utama di `agent/` menggabungkan tiga perubahan yang diminta:

| Bagian | Implementasi |
|---|---|
| Sampling | `temperature: 0` pada `configs/sampling.yaml`; top-p tetap 0.95 |
| Tool | Enam deklarasi: run_command, read_file, edit_file, write_file, get_status, submit_patch |
| Pemulihan | Bagian `TOOL ERROR RECOVERY` pada prompt; setelah dua kegagalan operasi yang sama, ganti pendekatan dan perbaiki argumen |

Dasarnya adalah V10 asli. Model 31B, thinking budget 4.096, output cap 8.192, batas 28 calls / 8 menit / 80 turns, dan timeout command 240 detik tetap sama. Perubahan prompt Verified V1 tidak dibawa ke kandidat baru. [Diff terhadap V10](combined_v2_prompt.diff) menunjukkan bagian prompt yang berubah.

Aturan pemulihan merupakan instruksi kepada Gemma, bukan penghitung runtime yang memaksa penghentian panggilan tool. Ini tetap sesuai format submission berbasis konfigurasi dan tool bawaan. Temperature 0 juga tidak menjamin skor identik pada semua kondisi serving.

Build dan validasi kandidat gabungan:

```powershell
python scripts/build.py
python scripts/generate_notebooks.py
python scripts/validate_compiler.py
python -m unittest discover -s tests -v
python scripts/submit.py --dry-run
```

Semua perintah default menunjuk kandidat yang sama. ZIP ada di `artifacts/submission.zip`, notebook mandiri di `notebooks/submission/submission.ipynb`, dan compiler receipt di `runs/validation/compiler.json`. [Manifest](../provenance/combined_v2.json) mengikat hash file dan arsip kandidat; jika sumber diubah untuk kandidat berikutnya, catat identitas artefak baru sebelum memperbarui hash manifest.

[Notebook Combined V2 di Kaggle](https://www.kaggle.com/code/adityaakbar/gemma-4-budget-aware-combined-v2) versi 1 sudah COMPLETE. ZIP output Kaggle cocok dengan build lokal dan telah dikirim sebagai submission `57626978`. Salinan dari server submission juga diunduh ulang dan identik. Snapshot 25 Oktober 2026 10:47:04 UTC masih menunggu penilaian, tanpa skor atau error evaluasi.

Compiler resmi memeriksa tool yang benar-benar terpasang dan temperature hasil kompilasi, kemudian menjalankan fixture read/edit/status/check/submit. Pemeriksaan ini tidak mengukur kemampuan Gemma pada task kompetisi. Hasil skor hanya dicatat setelah evaluasi nyata; skor historis V1 0.15, reproduksi V10 0.17, dan upstream 0.22 bukan hasil kandidat ini.

Metadata contoh `configs/kaggle/submission.example.json` memakai slug `gemma-4-budget-aware-combined-v2`. Isi username pada `notebooks/submission/kernel-metadata.json` lokal sebelum push. Notebook pengemas memakai CPU; evaluasi submission dijalankan oleh kompetisi. Notebook GPU opsional memakai sampling kandidat saat ini untuk pemeriksaan kompatibilitas.

Pengiriman nyata:

```powershell
python scripts/submit.py --credentials-file C:\private\kaggle.json
python scripts/status.py --credentials-file C:\private\kaggle.json
```

State sebelumnya disimpan ke `runs/history/` sebelum upload baru. Source V1 tetap dapat diambil dari commit historis yang tercatat pada `provenance/submitted_v1.json`; reproduksi V10 tetap dapat dibangun dengan `scripts/reproduce_public.py`.
