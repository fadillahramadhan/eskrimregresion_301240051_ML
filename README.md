# Prediksi Pendapatan Toko Es Krim dari Suhu (Regresi Linear Sederhana + Flask)

Proyek Akhir Modul 1. Dataset: Kaggle - Ice Cream Revenue (`Temperature` -> `Revenue`).

## Langkah menjalankan
```bash
pip install -r requirements.txt
# 1. taruh IceCreamData.csv di folder data/ (lihat data/README.md)
python train.py          # EDA, training, evaluasi, simpan model + grafik
python app.py            # buka http://127.0.0.1:5000
python build_report.py   # buat Laporan_Regresi_Linear.docx (isi dulu link di file)
```

## Deploy (Render)
- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn app:app`
- Commit juga folder `model/` dan `static/img/` hasil `train.py` agar app bisa jalan.

## Struktur
`train.py` (EDA+model) · `app.py` (Flask) · `templates/index.html` (Bootstrap) · `build_report.py` (laporan) · `Procfile` · `requirements.txt`
