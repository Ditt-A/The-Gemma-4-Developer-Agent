# The Gemma 4 Developer Agent

Proyek agen perbaikan kode untuk [Gemma 4 Developer Agent Competition](https://www.kaggle.com/competitions/gemma-4-developer-agent). Konfigurasi dan prompt utama ada di `agent/`; ZIP dan notebook dibangun dari sumber yang sama.

Eksperimen V1 di `agent/` memperoleh skor publik **0.15**. Reproduksi terpisah sekarang memakai empat file Budget-Aware V10 asli tanpa perubahan dan menghasilkan ZIP yang identik byte demi byte dengan artefak publiknya. Skor **0.22** adalah hasil upstream flexonafft V10; skor reproduksi kita dicatat setelah evaluasi Kaggle. Lihat [reproduksi V10](docs/reproduction_v10.md) dan [metode dan atribusi](docs/methodology.md).

```text
agent/                      # Sumber konfigurasi dan prompt yang dikirim
  agent.yaml
  eval_config.yaml
  configs/sampling.yaml
  prompts/system.md
scripts/                    # Build, generator notebook, validasi, submit, status
notebooks/
  submission/               # Notebook pembuat ZIP, tanpa output tersimpan
  gpu_smoke/                # Pemeriksaan serving di Kaggle L4x4
  reproduction_v10/         # Reproduksi persis artefak publik terbaik
templates/                  # Sumber sel notebook yang dapat diedit
configs/kaggle/             # Contoh metadata dengan username placeholder
tests/                      # Pemeriksaan portabilitas dan regresi
docs/                       # Metode, cara submit, dan catatan eksperimen
provenance/                 # Sumber upstream, manifest reproduksi, hash, atribusi
artifacts/                  # ZIP dan build receipt; diabaikan Git
runs/                       # Status, validasi, output, dan histori lokal; diabaikan Git
.local/                     # Wheel compiler dan referensi mesin ini; diabaikan Git
```

Siapkan Python 3.12+ dan Git. Contoh PowerShell dari root proyek:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Edit `agent/`, lalu bangun ZIP, perbarui notebook, dan jalankan pemeriksaan lokal:

```powershell
python scripts/build.py
python scripts/generate_notebooks.py
python -m unittest discover -s tests -v
python scripts/submit.py --dry-run
```

Hasil build ada di `artifacts/submission.zip`. Generator menghasilkan notebook mandiri yang dapat dijalankan di Kaggle tanpa mengimpor kode dari repo. Setelah mengubah `agent/` atau `templates/`, jalankan generator lagi sebelum menyimpan notebook ke repo.

Untuk membangun reproduksi upstream secara terpisah:

```powershell
python scripts/reproduce_public.py
```

Hasilnya `artifacts/reproduction_v10/submission.zip`, berukuran 3.713 byte dengan SHA-256 `6ff73d104725cc31deadd18787f3f55e5ce534889cec82387e3b280637d34887`. Script memverifikasi hash setiap file dan keseluruhan ZIP terhadap [manifest sumber](provenance/reproduction_v10.json). Notebook mandirinya ada di `notebooks/reproduction_v10/reproduction.ipynb`. Perintah validasi dan submit khusus reproduksi ada di [panduan reproduksi](docs/reproduction_v10.md).

Validasi compiler resmi dan alur tool ADK tersedia terpisah:

```powershell
python -m pip install -r requirements-compiler.txt
python scripts/validate_compiler.py
```

Wheel resmi harus tersedia di `.local/wheels/` terlebih dahulu. Sumber dan hash-nya ada di [manifest wheel](provenance/compiler_wheels.json). Detail instalasi dan pengiriman ada di [panduan submission](docs/submission.md).

Autentikasi hanya dibaca saat menjalankan operasi Kaggle. Gunakan konfigurasi standar Kaggle, environment variable, atau `--credentials-file` yang menunjuk file di luar repo. Contoh:

```powershell
python scripts/status.py --credentials-file C:\private\kaggle.json --id 57549113
```

`python scripts/submit.py` adalah tindakan upload nyata. Pengirim memeriksa ZIP dan receipt compiler untuk hash yang sama, menyimpan state sebelum upload, dan mencegah duplikasi saat hasil masih pending atau belum pasti. `COMPLETE` dengan `errorDescription` diperlakukan sebagai kegagalan.

Metadata akun lokal bernama `kernel-metadata.json`, kredensial, virtual environment, ZIP, wheel, log, dan raw receipt diabaikan Git. Contoh metadata di `configs/kaggle/` dapat dibagikan. Histori pengujian yang diringkas tersedia di [catatan eksperimen](docs/experiments.md); receipt lengkap tetap lokal.

Origin repo adalah `https://github.com/Ditt-A/The-Gemma-4-Developer-Agent.git`, branch `main`.

Lisensi Apache-2.0. Atribusi sumber dipertahankan dalam [NOTICE.txt](NOTICE.txt) dan arsip agen.
