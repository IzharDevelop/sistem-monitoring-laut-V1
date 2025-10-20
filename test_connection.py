import requests

url = "https://www.google.com"
print(f"Mencoba menghubungkan ke: {url}")

try:
    response = requests.get(url, timeout=10)
    print("\n--- KONEKSI BERHASIL ---")
    print(f"Status Code: {response.status_code}")
    print("Ini berarti Python di komputer Anda BISA terhubung ke internet dengan aman.")
    print("Jika ini berhasil tapi aplikasi utama masih gagal, kemungkinan ada masalah spesifik dengan library Gemini atau API key Anda.")

except requests.exceptions.SSLError as e:
    print("\n--- KONEKSI GAGAL: SSL ERROR ---")
    print("Ini adalah masalah yang paling umum.")
    print("Artinya, Python Anda kesulitan memverifikasi sertifikat keamanan (SSL) server Google.")
    print("Jangan khawatir, ini bisa diperbaiki dengan memperbarui pustaka sertifikat Anda.")
    # print(f"Detail Error: {e}") # Uncomment for full error details

except requests.exceptions.RequestException as e:
    print("\n--- KONEKSI GAGAL: KESALAHAN JARINGAN LAIN ---")
    print("Terjadi kesalahan koneksi umum di dalam Python.")
    print("Ini bisa jadi masalah proxy atau konfigurasi jaringan lain yang spesifik untuk Python.")
    # print(f"Detail Error: {e}") # Uncomment for full error details
