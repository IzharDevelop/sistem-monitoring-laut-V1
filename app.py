
import time
import re
import serial
import serial.tools.list_ports
import threading
from collections import deque
from flask import Flask, render_template, request, jsonify, redirect, url_for

# --- Konfigurasi dan Variabel Global ---
app = Flask(__name__)

# Variabel untuk menyimpan koneksi serial dan statusnya
ser = None
serial_thread = None
stop_thread = False
data_lock = threading.Lock()

# Variabel untuk menyimpan data sensor terakhir yang dibaca (diperluas)
latest_data = {
    "timestamp": None, "water": 0, "air": 0, "temp": 0,
    "gyro_right": 0, "gyro_left": 0, "level": 0, "conveyor": 0
}
# Deque untuk menyimpan log data serial mentah
raw_serial_log = deque(maxlen=20)

# --- Logika Backend: Pembacaan Data Serial di Background ---

def read_from_port():
    """Fungsi yang berjalan di background thread untuk membaca data dari serial."""
    global ser, latest_data, stop_thread, raw_serial_log
    
    # Pola regex diubah untuk mencocokkan format 7 nilai "angka,angka,..."
    pattern = re.compile(r"^(\d+),(\d+),(\d+),(\d+),(\d+),(\d+),(\d+)$")

    while not stop_thread and ser and ser.is_open:
        try:
            line = ser.readline().decode('utf-8').strip()
            
            with data_lock:
                if not line:
                    if not raw_serial_log or "[Timeout]" not in raw_serial_log[-1]:
                        raw_serial_log.append("[Timeout] Menunggu data dari port serial...")
                else:
                    raw_serial_log.append(f"> {line}")

            if not line:
                time.sleep(0.5)
                continue

            match = pattern.search(line)
            if match:
                timestamp = time.strftime('%H:%M:%S')
                
                with data_lock:
                    latest_data["timestamp"] = timestamp
                    latest_data["water"] = int(match.group(1))
                    latest_data["air"] = int(match.group(2))
                    latest_data["temp"] = int(match.group(3))
                    latest_data["gyro_right"] = int(match.group(4))
                    latest_data["gyro_left"] = int(match.group(5))
                    latest_data["level"] = int(match.group(6))
                    latest_data["conveyor"] = int(match.group(7))
            
            time.sleep(0.05)

        except (serial.SerialException, TypeError, UnicodeDecodeError) as e:
            error_msg = f"[ERROR] Terjadi masalah: {e}"
            print(error_msg)
            with data_lock:
                raw_serial_log.append(error_msg)
            stop_thread = True
            break
    print("Thread pembacaan serial dihentikan.")

# --- Rute-rute Aplikasi Flask ---

@app.route('/', methods=['GET', 'POST'])
def config_page():
    """Menampilkan halaman konfigurasi dan menangani submit form."""
    global ser, serial_thread, stop_thread

    if request.method == 'POST':
        port = request.form.get('port')
        baudrate = int(request.form.get('baudrate'))

        if ser and ser.is_open:
            stop_thread = True
            if serial_thread: serial_thread.join()
            ser.close()
            print("Koneksi serial lama ditutup.")

        try:
            ser = serial.Serial(port, baudrate, timeout=1)
            print(f"Terhubung ke {port} pada baudrate {baudrate}")
            
            stop_thread = False
            serial_thread = threading.Thread(target=read_from_port)
            serial_thread.daemon = True
            serial_thread.start()
            
            return redirect(url_for('dashboard_page'))

        except serial.SerialException as e:
            print(f"Gagal terhubung: {e}")
            ports = serial.tools.list_ports.comports()
            return render_template('config.html', ports=ports, error=str(e))

    ports = serial.tools.list_ports.comports()
    return render_template('config.html', ports=ports)

@app.route('/dashboard')
def dashboard_page():
    """Menampilkan halaman dashboard utama."""
    if not ser or not ser.is_open:
        return redirect(url_for('config_page'))
    return render_template('dashboard.html')

# --- Rute API untuk Frontend ---

@app.route('/data')
def get_data():
    """Endpoint API untuk mengirim data sensor terbaru ke frontend."""
    with data_lock:
        data_copy = latest_data.copy()
    return jsonify(data_copy)

@app.route('/serial_log')
def get_serial_log():
    """Endpoint API untuk mengirim log serial mentah ke frontend."""
    with data_lock:
        log_copy = list(raw_serial_log)
    return jsonify(log_copy)

@app.route('/control', methods=['POST'])
def control_device():
    """Endpoint API untuk menerima perintah kontrol dari frontend."""
    global ser
    req_data = request.get_json()
    state = req_data.get('state')
    
    if not ser or not ser.is_open:
        return jsonify({"status": "error", "message": "Port serial tidak terhubung"}), 500

    command = 'o' if state == 'on' else 'c' if state == 'off' else ''
    
    if command:
        try:
            with data_lock:
                ser.write(command.encode('utf-8'))
            print(f"Perintah '{command}' terkirim ke perangkat.")
            return jsonify({"status": "sukses", "command_sent": command})
        except serial.SerialException as e:
            print(f"Gagal mengirim perintah: {e}")
            return jsonify({"status": "error", "message": str(e)}), 500
            
    return jsonify({"status": "error", "message": "Perintah tidak valid"}), 400

# --- Menjalankan Aplikasi ---
if __name__ == '__main__':
    app.run(debug=True, threaded=True, use_reloader=False)
