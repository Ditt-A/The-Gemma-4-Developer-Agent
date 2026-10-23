# The Gemma 4 Developer Agent

Proyek agen perbaikan kode untuk [Gemma 4 Developer Agent Competition](https://www.kaggle.com/competitions/gemma-4-developer-agent). Konfigurasi dan prompt utama ada di `agent/`; ZIP dan notebook dibangun dari sumber yang sama.

Kandidat saat ini memakai satu agen Gemma 4 31B, sembilan tool bawaan, dan batas 28 tool calls / 8 menit per task. Kandidat mengadaptasi Budget-Aware V10 dengan verifikasi sesudah edit terakhir dan penyelesaian sesi yang lebih tegas. Skor publik 0.22 adalah hasil sumber upstream, bukan hasil kandidat ini. Lihat [metode dan atribusi](docs/methodology.md).

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
templates/                  # Sumber sel notebook yang dapat diedit
configs/kaggle/             # Contoh metadata dengan username placeholder
tests/                      # Pemeriksaan portabilitas dan regresi
docs/                       # Metode, cara submit, dan catatan eksperimen
provenance/                 # Sumber upstream, versi, hash, dan atribusi
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

Origin repo adalah `https://github.com/Ditt-A/The-Gemma-4-Developer-Agent.git`. Setelah meninjau file lokal, perintah untuk commit dan push nanti:

```powershell
git status --short
git add .
git commit -m "Organize Gemma 4 developer agent project"
git push -u origin main
```

Lisensi Apache-2.0. Atribusi sumber dipertahankan dalam [NOTICE.txt](NOTICE.txt) dan arsip agen.
