# PRAHU - Real-Time Monitoring and Control Dashboard

**PRAHU** adalah aplikasi web berbasis Flask yang dirancang untuk memonitor dan mengendalikan perangkat keras (seperti perahu purwarupa yang dilengkapi Arduino) secara *real-time* melalui komunikasi serial.

![Admin Dashboard Screenshot](img/admin_dashboard_preview.png)  
*(Catatan: Anda perlu menambahkan screenshot bernama `admin_dashboard_preview.png` di dalam folder `img/` agar gambar ini tampil)*

---

## Fitur Utama

- **Dasbor Admin Modern**: Antarmuka pengguna yang bersih dan responsif, dirancang untuk kemudahan penggunaan.
- **Kontrol Perangkat Komprehensif**:
  - **Navigasi**: Kontrol untuk belok kiri, kanan, dan lurus.
  - **Mesin**: Kontrol untuk maju dan berhenti.
  - **Sistem**: Kontrol untuk menyalakan dan mematikan konveyor.
- **Visualisasi Data Real-Time**: Grafik live untuk memonitor sensor-sensor penting (pH, polusi udara, suhu, level air).
- **Panel Status Terpusat**: Tampilan ringkas untuk status mesin, konveyor, arah belok, dan kemiringan perahu.
- **Live Serial Monitor**: Jendela untuk memantau data mentah yang masuk dari perangkat keras, sangat berguna untuk *debugging*.
- **Otentikasi Admin**: Halaman login sederhana untuk melindungi akses ke panel konfigurasi dan kontrol.
- **Konfigurasi Koneksi Mudah**: Antarmuka untuk memilih port serial dan *baud rate* saat aplikasi pertama kali dijalankan.
- **API Endpoints**: Menyediakan data dalam format JSON untuk kemungkinan integrasi dengan sistem lain.

---

## Struktur Proyek

```
/PRAHU
|-- app.py                  # File utama aplikasi Flask (logika backend)
|-- requirements.txt        # Daftar dependensi Python
|-- karyawan.json           # Database sederhana untuk login admin
|-- monitoring_data.json    # File log untuk menyimpan riwayat data sensor
|-- prahu_arduino/          # Contoh kode untuk perangkat keras (Arduino)
|   `-- prahu_arduino.ino
|-- templates/              # Folder untuk file HTML
|   |-- admin_login.html
|   |-- admin_config.html
|   |-- admin_dashboard.html
|   |-- documentation.html
|   `-- ... (halaman lainnya)
|-- img/                    # Folder untuk aset gambar
|-- .gitignore
`-- README.md
```

---

## Instalasi & Persyaratan

- Python 3.x
- Pyserial & Flask

1.  **Clone Repositori**
    ```bash
    git clone <url-repositori-anda>
    cd PRAHU
    ```

2.  **Buat dan Aktifkan Virtual Environment** (Direkomendasikan)
    ```bash
    # Windows
    python -m venv .venv
    .venv\Scripts\activate

    # macOS/Linux
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3.  **Instal Dependensi**
    Pastikan Anda berada di direktori utama proyek, lalu jalankan:
    ```bash
    pip install -r requirements.txt
    ```

---

## Menjalankan Aplikasi

1.  Pastikan perangkat keras Anda terhubung ke komputer.
2.  Jalankan server Flask dengan perintah:
    ```bash
    python app.py
    ```
3.  Buka browser dan kunjungi `http://127.0.0.1:5000`.
4.  Anda akan diarahkan ke halaman login admin. Gunakan kredensial dari `karyawan.json` (contoh: `admin`/`admin`).
5.  Setelah login, pilih Port COM dan Baud Rate yang sesuai dengan perangkat Anda, lalu klik "Hubungkan".

---

## Format Data Serial Perangkat Keras

Aplikasi mengharapkan perangkat keras mengirim data melalui serial dalam format yang spesifik: **9 nilai integer yang dipisahkan koma**, diakhiri dengan *newline* (`\n`).

Gunakan `Serial.println()` pada Arduino untuk memastikan format ini terpenuhi.

**Urutan Data:**
`TDS,Udara,Suhu,GiroKanan,GiroKiri,LevelAir,Konveyor,Belok,Maju`

**Contoh Baris Data:** `531,432,28,0,0,988,0,0,0`

| Urutan | Deskripsi         | Contoh | Keterangan                                    |
| :----: | ----------------- | :----: | --------------------------------------------- |
| 1      | Kualitas Air (TDS)| `531`  | Nilai mentah dari sensor TDS/pH.              |
| 2      | Kualitas Udara    | `432`  | Nilai mentah dari sensor polusi udara.        |
| 3      | Suhu              | `28`   | Nilai mentah dari sensor suhu.                |
| 4      | Giro Kanan        | `0`    | Nilai dari sensor giroskop (sumbu kanan).     |
| 5      | Giro Kiri         | `0`    | Nilai dari sensor giroskop (sumbu kiri).      |
| 6      | Level Air         | `988`  | Nilai mentah dari sensor level air.           |
| 7      | Status Konveyor   | `0`    | `1` jika ON, `0` jika OFF.                    |
| 8      | Status Belok      | `0`    | Derajat belok (misal: -90, 0, 90).            |
| 9      | Status Maju       | `0`    | `1` jika mesin maju, `0` jika berhenti.       |

Lihat `prahu_arduino/prahu_arduino.ino` untuk contoh implementasi pada Arduino.