# Catatan eksperimen

Catatan ini merupakan ringkasan historis, bukan status live Kaggle. Gunakan `python scripts/status.py` untuk memperbarui receipt lokal.

| Tanggal | Pemeriksaan | Hasil tercatat |
|---|---|---|
| 22 Oktober 2026 | Compiler adk-submission 0.2.13 / ADK 1.36.1 | Lulus; fixture alur read/edit/check/submit lulus |
| 22 Oktober 2026 | Notebook pengemas V1 | COMPLETE; ZIP terverifikasi |
| 22 Oktober 2026 | GPU smoke L4x4, sesi 300 detik | Berhenti saat pemuatan checkpoint; belum menguji inferensi |
| 22 Oktober 2026 | Submission `57529425`, jalur notebook | Gagal saat rerun; skor tidak tersedia |
| 22 Oktober 2026 | Notebook pengemas V2, ceiling 43.200 detik | COMPLETE; isi ZIP identik |
| 23 Oktober 2026 | Submission `57549113`, unggahan ZIP langsung | Diterima; snapshot terakhir 04:32:49 UTC belum memuat error atau skor |

ZIP V1 memiliki SHA-256 `a5f2c86dd33bf107724515db42002ebc3c7a330cbd1e69fc0fe84f63b4b76d8d`. Saat struktur repo disusun ulang, build dari `agent/` menghasilkan arsip yang identik, termasuk byte ZIP. Pemeriksaan ini melindungi identitas artefak selama restrukturisasi dan tidak mengukur kualitas agen.

Penyebab internal kegagalan rerun pertama belum terkonfirmasi karena API tidak menyediakan traceback scorer. [Audit format](submission_error_review.id.md) mencatat fakta yang terverifikasi. File lengkap dan receipt impor disimpan lokal di `runs/imported_20261023/`; state pengiriman terbaru ada di `runs/state/submission.json`.

Hasil compiler, output model, dan skor perlu dicatat terpisah. Status COMPLETE dengan error bukan hasil sukses; benchmark lokal dengan model terprogram bukan hasil kualitas Gemma; skor upstream bukan skor kandidat ini.
