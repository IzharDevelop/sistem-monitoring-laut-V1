
# Real-Time Sensor Monitoring Dashboard

Ini adalah aplikasi web berbasis Flask yang berfungsi sebagai dasbor untuk memonitoring dan mengontrol perangkat keras (seperti Arduino) secara real-time melalui komunikasi serial.

## Fitur Utama

- **Dasbor Real-Time**: Menampilkan data sensor yang masuk secara langsung tanpa perlu me-refresh halaman.
- **4 Grafik Sensor**: Visualisasi data untuk Kualitas Air (pH), Kualitas Udara, Suhu, dan Level Air dengan skala 0-1023.
- **Jendela Waktu Terfokus**: Grafik hanya menampilkan 10 titik data terakhir untuk memantau perubahan terkini.
- **Panel Status**: Indikator visual untuk status kemiringan perangkat (Center, Kanan, Kiri) dan status konveyor (ON/OFF).
- **Kontrol Perangkat**: Tombol interaktif untuk menyalakan (`o`) dan mematikan (`c`) konveyor langsung dari halaman web.
- **Live Serial Monitor**: Menampilkan data mentah yang diterima dari perangkat serial untuk keperluan debugging.
- **Konfigurasi Mudah**: Halaman awal untuk memilih Port COM dan Baud Rate dengan mudah.

---

## Persyaratan

- Python 3.x
- Pustaka Python yang tercantum dalam `requirements.txt`

## Instalasi

1.  Clone atau unduh repositori ini.
2.  Buka terminal atau command prompt di dalam direktori proyek.
3.  Instal semua pustaka yang dibutuhkan dengan menjalankan:
    ```bash
    pip install -r requirements.txt
    ```

---

## Pengaturan Perangkat Keras & Format Data Serial

Aplikasi ini mengharapkan perangkat keras Anda (misalnya Arduino) untuk mengirim data melalui koneksi serial dengan format yang sangat spesifik.

**PENTING:** Data harus dikirim sebagai **satu baris teks (string)**, dengan **7 nilai angka** yang dipisahkan oleh koma, dan diakhiri dengan **baris baru (newline)**. Gunakan `Serial.println()` di Arduino, bukan `Serial.print()`.

### Urutan Data Serial

Berikut adalah urutan nilai yang harus dikirim:

`[Nilai_pH],[Nilai_Udara],[Nilai_Suhu],[Giro_Kanan],[Giro_Kiri],[Level_Air],[Status_Konveyor]`

**Contoh Baris Data:** `7,450,28,0,0,800,1`

| Urutan | Deskripsi         | Contoh Nilai | Keterangan                                                               |
| :----: | ----------------- | :----------: | ------------------------------------------------------------------------ |
| 1      | Kualitas Air (pH) | `7`          | Akan ditampilkan di grafik "Kualitas Air".                               |
| 2      | Kualitas Udara    | `450`        | Akan ditampilkan di grafik "Kualitas Udara".                             |
| 3      | Suhu              | `28`         | Akan ditampilkan di grafik "Suhu".                                       |
| 4      | Giro Kanan        | `90`         | Jika nilai > 0, status akan menjadi "Miring Kanan".                      |
| 5      | Giro Kiri         | `0`          | Jika nilai > 0 (dan Giro Kanan = 0), status akan menjadi "Miring Kiri". |
| 6      | Level Air         | `800`        | Akan ditampilkan di grafik "Level Air".                                  |
| 7      | Status Konveyor   | `1`          | `1` untuk ON, `0` untuk OFF.                                             |


### Contoh Kode Arduino

Anda bisa menggunakan kode ini sebagai referensi untuk perangkat keras Anda.

```cpp
void setup() {
  Serial.begin(9600); // Pastikan baud rate sama dengan yang dipilih di web
}

void loop() {
  // Ganti nilai-nilai ini dengan pembacaan sensor Anda yang sebenarnya
  int nilai_pH = 7;
  int nilai_udara = 450;
  int nilai_suhu = 28;
  int nilai_giro_kanan = 0;
  int nilai_giro_kiri = 0;
  int nilai_level_air = 800;
  int status_konveyor = 1;

  // Bangun satu String lengkap dengan semua data
  String data_kirim = String(nilai_pH) + "," + String(nilai_udara) + "," + String(nilai_suhu) + "," + 
                      String(nilai_giro_kanan) + "," + String(nilai_giro_kiri) + "," + String(nilai_level_air) + "," + 
                      String(status_konveyor);

  // Kirim String dengan SATU perintah println
  Serial.println(data_kirim);

  // Jeda sebelum pengiriman data berikutnya
  delay(2000); // Kirim data setiap 2 detik
}
```

---

## Cara Menjalankan Aplikasi

1.  Pastikan perangkat keras Anda terhubung ke komputer.
2.  Jalankan server Flask dengan perintah:
    ```bash
    python app.py
    ```
3.  Buka browser web Anda dan kunjungi alamat:
    `http://127.0.0.1:5000`

## Cara Menggunakan

1.  Pada halaman awal, pilih **Port COM** yang sesuai dengan perangkat Anda.
2.  Pilih **Baud Rate** yang sesuai dengan pengaturan di kode perangkat keras Anda (contoh di atas menggunakan **9600**).
3.  Klik tombol **"Hubungkan"**.
4.  Anda akan diarahkan ke dasbor utama di mana Anda bisa melihat data secara real-time.
5.  Gunakan tombol **"Nyalakan"** atau **"Matikan"** di panel status untuk mengirim perintah ke konveyor Anda.
