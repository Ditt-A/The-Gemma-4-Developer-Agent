# Metode dan sumber

Kandidat utama `budget-aware-combined-v2` menggabungkan tiga perubahan dalam satu agen, memakai [Budget-Aware V10 milik flexonafft](https://www.kaggle.com/code/flexonafft/gemma-4-budget-aware-coding-agent-v2?scriptVersionId=357955943) sebagai dasar: temperature 0, penghapusan tiga deklarasi tool graph, dan instruksi pemulihan error tool berulang. Konfigurasi aktif berada di `agent/`; tidak ada tiga varian terpisah untuk perubahan ini.

| Pengaturan | Kandidat |
|---|---|
| Base model | `gemma-4-31b-it-qat-w4a16-ct` |
| Arsitektur | Satu agen; tanpa LoRA atau skill tambahan |
| Temperature / top-p | 0 / 0.95 |
| Tool | run_command, read_file, edit_file, write_file, get_status, submit_patch |
| Output cap | 8.192 token |
| Thinking budget | 4.096; thoughts disertakan |
| Batas task | 28 calls, 8 menit, 80 turns |
| Timeout command | 240 detik |

Prompt memulai perbaikan dari nama API, path, pesan error, atau simbol pada issue. Pencarian yang independen digabung; pembacaan dibatasi pada implementasi dan caller atau tes yang relevan. Edit menggunakan anchor pendek yang unik. Setelah kegagalan pencocokan berulang, prompt meminta satu penggantian teks yang dijaga oleh assertion, lalu verifikasi terarah.

Bagian baru `TOOL ERROR RECOVERY` meminta agen membaca error dan mengubah argumen atau pendekatan. Setelah dua kegagalan operasi yang sama, agen harus memakai alternatif yang lebih sederhana: konfirmasi path dan baca terbatas melalui shell untuk kegagalan read_file, perbaiki quoting atau argumen pada run_command, serta fallback inline Python dengan assertion untuk kegagalan edit_file. Tes boleh diulang setelah sumber atau penyebab kegagalannya diperbaiki. Pemulihan memakai anggaran yang sama, dengan ruang untuk diff dan submit.

Instruksi ini berada di prompt, bukan callback runtime yang memblokir panggilan ketiga. Compiler dan fixture ADK memastikan konfigurasi dan alur tool dapat dijalankan; keduanya tidak membuktikan bahwa Gemma selalu mematuhi instruksi atau bahwa skor naik. Karena ketiga perubahan digabung, hasil evaluasinya juga tidak mengisolasi efek masing-masing perubahan.

Eksperimen historis Verified V1 memakai tambahan checkpoint verifikasi dari [E05 milik prvsiyan](https://www.kaggle.com/code/prvsiyan/gemma-and-the-shape-of-doubt?scriptVersionId=359522074) dan memperoleh skor 0.15. Tambahan prompt V1 itu tidak menjadi dasar Combined V2. [Reproduksi V10 tanpa perubahan](reproduction_v10.md) memperoleh 0.17 dan tetap tersedia sebagai baseline historis.

Snapshot riset 22 Oktober 2026 membandingkan 100 notebook dan 25 arsip submission. [Laporan metode](research/methods_review_20261022.id.md), [ranking CSV](research/code_ranking_20261022.csv), dan [ringkasan bundle](research/bundle_summary_20261022.json) menyimpan konteks pengamatan tersebut. Skor yang sama dan arsip yang identik tidak membuktikan efek kausal suatu teknik; beberapa arsip identik mendapat skor berbeda.

Empat file upstream disimpan sebagai referensi berlisensi di `provenance/upstream/budget_aware_v10/`. Sumber kandidat yang diedit untuk build adalah `agent/`. [Manifest Combined V2](../provenance/combined_v2.json) mencatat hash kandidat; [diff prompt Combined V2](combined_v2_prompt.diff) memperlihatkan perubahan terhadap V10. [Manifest V1](../provenance/submitted_v1.json) dan [diff V1](prompt_changes.diff) tetap menjadi catatan historis.

Notebook GPU mengadaptasi setup dari [starter resmi Ryan Holbrook](https://www.kaggle.com/code/ryanholbrook/getting-started-gemma-4-developer-agent). Notebook ini hanya memeriksa serving dan satu panggilan tool. Penilaian kualitas patch membutuhkan benchmark yang terpisah.
