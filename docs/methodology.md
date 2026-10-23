# Metode dan sumber

Kandidat `budget-aware-verified-v1` mempertahankan model, sampling, sembilan deklarasi tool, serta anggaran dari [Budget-Aware V10 milik flexonafft](https://www.kaggle.com/code/flexonafft/gemma-4-budget-aware-coding-agent-v2?scriptVersionId=357955943). Prompt diperbarui untuk menyimpan satu pemeriksaan setelah edit terakhir, menjaga exit status tes, memakai aturan protected file terbaru, dan mengakhiri sesi sesudah submit.

| Pengaturan | Kandidat |
|---|---|
| Base model | `gemma-4-31b-it-qat-w4a16-ct` |
| Arsitektur | Satu agen; tanpa LoRA atau skill tambahan |
| Temperature / top-p | 0.2 / 0.95 |
| Output cap | 8.192 token |
| Thinking budget | 4.096; thoughts disertakan |
| Batas task | 28 calls, 8 menit, 80 turns |
| Timeout command | 240 detik |

Prompt memulai perbaikan dari nama API, path, pesan error, atau simbol pada issue. Pencarian yang independen digabung; pembacaan dibatasi pada implementasi dan caller atau tes yang relevan. Edit menggunakan anchor pendek yang unik. Setelah kegagalan pencocokan berulang, prompt meminta satu penggantian teks yang dijaga oleh assertion, lalu verifikasi terarah.

Checkpoint verifikasi terakhir terinspirasi oleh [E05 milik prvsiyan](https://www.kaggle.com/code/prvsiyan/gemma-and-the-shape-of-doubt?scriptVersionId=359522074). Ini merupakan hipotesis perbaikan alur, belum merupakan hasil ablation yang terukur pada kandidat ini.

Snapshot riset 22 Oktober 2026 membandingkan 100 notebook dan 25 arsip submission. [Laporan metode](research/methods_review_20261022.id.md), [ranking CSV](research/code_ranking_20261022.csv), dan [ringkasan bundle](research/bundle_summary_20261022.json) menyimpan konteks pengamatan tersebut. Skor yang sama dan arsip yang identik tidak membuktikan efek kausal suatu teknik; beberapa arsip identik mendapat skor berbeda.

Empat file upstream disimpan sebagai referensi berlisensi di `provenance/upstream/budget_aware_v10/`. Sumber kandidat yang diedit untuk build adalah `agent/`. [Manifest kandidat](../provenance/submitted_v1.json) mencatat hash file dan arsip historis; [diff prompt](prompt_changes.diff) menunjukkan perubahan awal.

Notebook GPU mengadaptasi setup dari [starter resmi Ryan Holbrook](https://www.kaggle.com/code/ryanholbrook/getting-started-gemma-4-developer-agent). Notebook ini hanya memeriksa serving dan satu panggilan tool. Penilaian kualitas patch membutuhkan benchmark yang terpisah.
