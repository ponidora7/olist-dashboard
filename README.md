# 📊 Proyek Analisis Data: E-Commerce Public Dataset (Olist)

Proyek akhir analisis data menggunakan **Olist E-Commerce Public Dataset** yang mencakup
data transaksi e-commerce Brasil dari Oktober 2016 hingga Oktober 2018.

---

## 🗂️ Struktur Folder

```
submission/
├── dashboard.py                        ← Streamlit dashboard
├── requirements.txt                    ← Dependensi Python
├── README.md                           ← Panduan ini
└── main_data.csv
└── rfm_data.csv

                             
    
```

---

## ❓ Pertanyaan Bisnis (SMART Questions)

| # | Pertanyaan |
|---|-----------|
| 1 | **Kategori produk apa yang menghasilkan total revenue tertinggi**, dan bagaimana tren pendapatannya secara bulanan dari Oktober 2016 hingga Oktober 2018 pada platform Olist? |
| 2 | **Bagaimana hubungan antara keterlambatan pengiriman (delay dalam hari)** terhadap rata-rata skor ulasan pelanggan pada pesanan berstatus *delivered* sepanjang 2017–2018 di platform Olist? |

---

## 🚀 Cara Menjalankan Dashboard

### 1. Clone / Ekstrak project
```bash
unzip submission.zip -d submission/
cd submission/
```

### 2. Salin dataset ke folder `data/`
```bash
mkdir data
# Salin semua file CSV ke dalam folder data/
cp path/to/dataset/*.csv data/
```

### 3. Install dependensi
```bash
pip install -r requirements.txt
```

### 4. Jalankan dashboard Streamlit
```bash
streamlit run dashboard.py
```

Dashboard akan terbuka otomatis di browser pada `http://localhost:8501`

---



## 🔍 Ringkasan Temuan

### Pertanyaan 1 — Revenue per Kategori
- **health_beauty** adalah kategori dengan revenue tertinggi (BRL ~1,23 juta)
- Lima kategori teratas menyumbang **±28%** total revenue platform
- Lonjakan permintaan konsisten pada **November** (Black Friday Brasil)

### Pertanyaan 2 — Delay vs Review Score
- Korelasi negatif antara delay dan skor ulasan (**r = −0,27**)
- Titik kritis: delay **> 3 hari** menyebabkan skor rata-rata turun dari 3,77 → 2,32
- **76%** pesanan berhasil dikirim tepat waktu atau lebih cepat dari estimasi

---

## 📋 Dependensi Utama

| Library | Versi | Kegunaan |
|---------|-------|----------|
| pandas | 2.2.2 | Manipulasi data |
| numpy | 1.26.4 | Komputasi numerik |
| matplotlib | 3.9.0 | Visualisasi |
| seaborn | 0.13.2 | Visualisasi statistik |
| streamlit | 1.35.0 | Dashboard interaktif |
