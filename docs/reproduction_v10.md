# Reproduksi persis Budget-Aware V10

Pada 24 Oktober 2026, [Code publik yang diurutkan berdasarkan skor](https://www.kaggle.com/competitions/gemma-4-developer-agent/code) masih menempatkan [flexonafft V10](https://www.kaggle.com/code/flexonafft/gemma-4-budget-aware-coding-agent-v2?scriptVersionId=357955943) di posisi pertama dengan skor 0.22. API view notebook menghubungkan skor itu dengan versi 10, script version ID `357955943`, dan submission upstream `57139437`.

ZIP output dari versi tersebut diunduh ulang dan dibandingkan dengan build dari empat file di `provenance/upstream/budget_aware_v10/`. Hasilnya identik byte demi byte: 3.713 byte, SHA-256 `6ff73d104725cc31deadd18787f3f55e5ce534889cec82387e3b280637d34887`. Prompt, konfigurasi, sampling, anggaran, urutan member, metadata ZIP dan isi file dipertahankan. Lisensi dan atribusi ada di root repo dan pengantar notebook agar arsip aslinya tetap identik.

| Eksperimen | Artefak | Skor publik |
|---|---|---|
| V1 kita | SHA `a5f2c86dd33bf107...`, submission `57549113` | **0.15** |
| Upstream flexonafft V10 | SHA `6ff73d104725cc31...`, versi 10 | **0.22** |
| Reproduksi V10 kita | SHA sama persis, submission `57577673` | Diterima; menunggu evaluasi saat diperiksa 24 Oktober 01:08:29 UTC |

Skor upstream belum menjadi hasil reproduksi kita. Riwayat riset juga menunjukkan arsip identik dapat memperoleh skor berbeda, sehingga selisih V1 tidak langsung menjelaskan pengaruh perubahan prompt.

[Notebook reproduksi di Kaggle](https://www.kaggle.com/code/adityaakbar/gemma-4-budget-aware-v10-exact-reproduction) versi 1 sudah COMPLETE. ZIP hasil notebook diunduh, dibandingkan dengan artefak upstream dan build lokal, lalu dikirim langsung sebagai submission `57577673`. Salinan ZIP yang tersimpan di server submission juga diunduh ulang dan terbukti identik. Belum ada skor atau error evaluasi dalam snapshot terakhir tersebut.

Dari root repo:

```powershell
python scripts/reproduce_public.py
python scripts/generate_notebooks.py
python scripts/validate_compiler.py --agent-dir provenance/upstream/budget_aware_v10 --output-dir artifacts/reproduction_v10 --receipt runs/validation/reproduction_v10_compiler.json --candidate-id budget-aware-v10-exact-reproduction
python -m unittest discover -s tests -v
```

Compiler dan fixture ADK memeriksa format dan alur tool; kualitas patch diukur melalui evaluasi kompetisi. ZIP reproduksi tidak berisi modifikasi prompt V1 atau dua file lisensi tambahan dari paket V1.

Untuk menjalankan notebook pengemas di Kaggle:

```powershell
Copy-Item configs/kaggle/reproduction_v10.example.json notebooks/reproduction_v10/kernel-metadata.json
# Isi YOUR_KAGGLE_USERNAME pada metadata lokal.
python scripts/notebooks.py --credentials-file C:\private\kaggle.json push --folder notebooks/reproduction_v10 --timeout 43200
```

Notebook pengemas memakai CPU dan internet nonaktif. Inferensi Gemma untuk submission dijalankan oleh evaluasi kompetisi. Notebook memeriksa setiap member dan hash ZIP akhir; outputnya harus sama dengan artefak publik sumber.

Perintah berikut mengunggah ZIP nyata dan menghabiskan jatah submission. Ganti path arsip dengan hasil notebook yang telah diunduh bila diperlukan:

```powershell
python scripts/submit.py --archive artifacts/reproduction_v10/submission.zip --agent-dir provenance/upstream/budget_aware_v10 --compiler-receipt runs/validation/reproduction_v10_compiler.json --candidate-id budget-aware-v10-exact-reproduction --description "Exact public Budget-Aware V10 reproduction" --expected-sha256 6ff73d104725cc31deadd18787f3f55e5ce534889cec82387e3b280637d34887 --credentials-file C:\private\kaggle.json
python scripts/status.py --credentials-file C:\private\kaggle.json
```

Guard duplikasi berlaku lintas eksperimen. State submission sebelumnya disalin ke `runs/history/` sebelum pengiriman baru, sehingga hasil V1 tetap tersimpan. Identitas publik dan hasil reproduksi terpisah ada di [manifest](../provenance/reproduction_v10.json); data mentah API dan URL download sementara tetap lokal.
