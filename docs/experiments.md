# Catatan eksperimen

Catatan ini merupakan ringkasan historis, bukan status live Kaggle. Gunakan `python scripts/status.py` untuk memperbarui receipt lokal.

| Tanggal | Pemeriksaan | Hasil tercatat |
|---|---|---|
| 22 Oktober 2026 | Compiler adk-submission 0.2.13 / ADK 1.36.1 | Lulus; fixture alur read/edit/check/submit lulus |
| 22 Oktober 2026 | Notebook pengemas V1 | COMPLETE; ZIP terverifikasi |
| 22 Oktober 2026 | GPU smoke L4x4, sesi 300 detik | Berhenti saat pemuatan checkpoint; belum menguji inferensi |
| 22 Oktober 2026 | Submission `57529425`, jalur notebook | Gagal saat rerun; skor tidak tersedia |
| 22 Oktober 2026 | Notebook pengemas V2, ceiling 43.200 detik | COMPLETE; isi ZIP identik |
| 23 Oktober 2026 | Submission `57549113`, unggahan ZIP langsung | Selesai dengan skor publik **0.15**, dikonfirmasi 24 Oktober pukul 01:02:12 UTC |
| 24 Oktober 2026 | Peringkat Code publik diperbarui | flexonafft V10 masih tertinggi, **0.22**; versi tepat `357955943` |
| 24 Oktober 2026 | Reproduksi artefak publik V10 | ZIP 3.713 byte identik, SHA-256 `6ff73d104725cc31deadd18787f3f55e5ce534889cec82387e3b280637d34887`; compiler resmi dan fixture tool lulus |
| 24 Oktober 2026 | Notebook reproduksi versi 1 | COMPLETE; ZIP hasil Kaggle identik dengan output publik sumber |
| 24 Oktober 2026 | Submission reproduksi `57577673` | Diterima pukul 01:08:01 UTC; ZIP tersimpan di server identik; snapshot 01:08:29 UTC belum memuat error atau skor |

ZIP V1 memiliki SHA-256 `a5f2c86dd33bf107724515db42002ebc3c7a330cbd1e69fc0fe84f63b4b76d8d`. Saat struktur repo disusun ulang, build dari `agent/` menghasilkan arsip yang identik, termasuk byte ZIP. Pemeriksaan ini melindungi identitas artefak selama restrukturisasi dan tidak mengukur kualitas agen.

Penyebab internal kegagalan rerun pertama belum terkonfirmasi karena API tidak menyediakan traceback scorer. [Audit format](submission_error_review.id.md) mencatat fakta yang terverifikasi. File lengkap dan receipt impor disimpan lokal di `runs/imported_20261023/`; state pengiriman terbaru ada di `runs/state/submission.json`.

Hasil compiler, output model, dan skor perlu dicatat terpisah. Status COMPLETE dengan error bukan hasil sukses; benchmark lokal dengan model terprogram bukan hasil kualitas Gemma; skor upstream bukan skor kandidat ini.

Selisih skor 0.15 versus upstream 0.22 belum membuktikan perubahan prompt V1 sebagai penyebabnya. Reproduksi byte identik dipakai sebagai pembanding sebelum mencoba perubahan lebih lanjut. [Manifest reproduksi](../provenance/reproduction_v10.json) menyimpan identitas sumber, sedangkan [snapshot ranking baru](research/public_code_ranking_20261024.json) merekam urutan Code publik saat diperiksa.
