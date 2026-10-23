# Build, validasi, dan pengiriman

Jalankan semua perintah dari root repo, atau panggil script memakai path absolut. Script menentukan lokasi proyek dari filenya sendiri sehingga build tidak bergantung pada working directory.

```powershell
python scripts/build.py
python scripts/generate_notebooks.py
python -m unittest discover -s tests -v
```

`agent/` adalah sumber ZIP. Jangan mengedit dictionary `FILES` dalam notebook hasil generator: perubahan tersebut akan ditimpa pada generasi berikutnya. Sel notebook yang dapat diedit tersimpan di `templates/`.

Paket hasil build harus memiliki konfigurasi agen di root, include yang valid, ekstensi yang diperbolehkan, serta ukuran setelah ekstraksi di bawah 3 GiB. Pemeriksaan ringan dilakukan oleh `scripts/build.py`; validasi compiler dan fixture ADK dilakukan oleh `scripts/validate_compiler.py`. Fixture memakai model terprogram dan repository contoh yang terisolasi. Hasilnya memverifikasi integrasi, bukan kemampuan Gemma memperbaiki task.

Untuk memasang compiler resmi, unduh wheel berikut dari [wheelhouse penyelenggara](https://www.kaggle.com/datasets/metric/gemma-4-developer-agent-wheelhouse) ke `.local/wheels/`:

- `adk_submission-0.2.13-py3-none-any.whl`
- `google_adk-1.36.1-py3-none-any.whl`

```powershell
python -m pip install -r requirements-compiler.txt
python scripts/validate_compiler.py
```

Receipt ditulis ke `runs/validation/compiler.json` dan terikat pada hash ZIP. Perubahan prompt atau konfigurasi memerlukan validasi ulang sebelum upload.

Autentikasi menggunakan mekanisme standar Kaggle atau flag `--credentials-file` yang menunjuk JSON `username`/`key` di luar repo. Build, generator, pengujian lokal, bantuan CLI, dan dry run tidak memerlukan kredensial. Tidak ada script yang membaca otomatis folder Downloads.

```powershell
python scripts/submit.py --dry-run
python scripts/submit.py --credentials-file C:\private\kaggle.json
python scripts/status.py --credentials-file C:\private\kaggle.json
```

Upload menggunakan `KaggleApi.competition_submit` dengan file `submission.zip`. Receipt server dicatat sebagai `SUBMITTED_AWAITING_RESULT`, belum sebagai hasil penilaian. `scripts/status.py` memeriksa `errorDescription` terlebih dahulu dan menerima skor nol sebagai skor yang sah. State pending atau network uncertainty mengunci pengiriman duplikat; jalankan status untuk merekonsiliasi state. Retry hasil yang gagal memerlukan pemeriksaan penyebab, jatah harian yang tersedia, dan flag `--retry-failed`.

Untuk notebook Kaggle, salin contoh metadata ke folder notebook dan isi username akun:

```powershell
Copy-Item configs/kaggle/submission.example.json notebooks/submission/kernel-metadata.json
Copy-Item configs/kaggle/gpu_smoke.example.json notebooks/gpu_smoke/kernel-metadata.json
```

File `kernel-metadata.json` yang berisi konfigurasi akun diabaikan Git. Setelah mengedit `id` dan memeriksa input yang diperlukan, operasi berikut merupakan tindakan nyata di Kaggle:

```powershell
python scripts/notebooks.py --credentials-file C:\private\kaggle.json push --folder notebooks/submission --timeout 43200
python scripts/notebooks.py --credentials-file C:\private\kaggle.json status YOUR_KAGGLE_USERNAME/gemma-4-budget-aware-verified-v1
```

Notebook `gpu_smoke` memerlukan `metric/gemma-4-developer-agent-wheelhouse`, model Gemma 4 31B versi 2, L4x4, dan internet nonaktif. Runtime startup server default adalah 1.200 detik; notebook perlu waktu untuk instalasi dan pemuatan model. Contoh sesi pemeriksaan:

```powershell
python scripts/notebooks.py --credentials-file C:\private\kaggle.json quota
python scripts/notebooks.py --credentials-file C:\private\kaggle.json push --folder notebooks/gpu_smoke --accelerator NvidiaL4 --timeout 2700
```

Batas 8 menit adalah batas per task dalam agen. Batas 12 jam adalah batas keseluruhan penilaian kompetisi dan juga ceiling yang dipakai untuk notebook pengemas. Keduanya berbeda dari timeout sesi GPU smoke.
