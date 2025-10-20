import time
import re
import serial
import serial.tools.list_ports
import threading
import secrets
import json
from datetime import datetime
from collections import deque
from flask import Flask, render_template, request, jsonify, redirect, url_for, session

# --- Konfigurasi dan Variabel Global ---
app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
DATA_FILE = 'monitoring_data.json'
USER_FILE = 'karyawan.json'



ser = None
serial_thread = None
stop_thread = False
data_lock = threading.Lock()

current_port = None
current_baudrate = None

latest_data = {
    "timestamp": None,
    "raw": { "water": 0, "air": 0, "temp": 0, "gyro_right": 0, "gyro_left": 0, "level": 0, "conveyor": 0, "belok": 0, "maju": 0 },
    "converted": { "ph": 0, "pollution": 0, "celsius": 0, "water_level": 0 }
}
raw_serial_log = deque(maxlen=20)




# --- Logika Konversi & Backend ---

def convert_raw_to_real(raw_data):
    converted = {}
    converted['ph'] = round(raw_data['water'] / 1023 * 14, 1)
    converted['pollution'] = round(raw_data['air'] / 1023 * 100, 1)
    converted['celsius'] = round(raw_data['temp'] / 1023 * 100, 1)
    converted['water_level'] = round(raw_data['level'] / 1023 * 100, 1)
    return converted

def read_from_port():
    global ser, latest_data, stop_thread, raw_serial_log
    pattern = re.compile(r"^(\d+),(\d+),(\d+),(\d+),(\d+),(\d+),(\d+),(\d+),(\d+)$")
    while not stop_thread and ser and ser.is_open:
        try:
            line = ser.readline().decode('utf-8').strip()
            with data_lock:
                raw_serial_log.append(f"> {line}" if line else "[Timeout] Menunggu data...")
            if not line:
                time.sleep(0.5)
                continue
            match = pattern.search(line)
            if match:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                raw_values = {
                    "water": int(match.group(1)),
                    "air": int(match.group(2)),
                    "temp": int(match.group(3)),
                    "gyro_right": int(match.group(4)),
                    "gyro_left": int(match.group(5)),
                    "level": int(match.group(6)),
                    "conveyor": int(match.group(7)),
                    "belok": int(match.group(8)),
                    "maju": int(match.group(9))
                }
                with data_lock:
                    latest_data["timestamp"] = timestamp
                    latest_data["raw"] = raw_values
                    latest_data["converted"] = convert_raw_to_real(raw_values)
                    try:
                        with open(DATA_FILE, 'r+', encoding='utf-8') as f:
                            records = json.load(f)
                            records.append(latest_data)
                            f.seek(0)
                            f.truncate()
                            json.dump(records, f, indent=4)
                    except (FileNotFoundError, json.JSONDecodeError):
                        print(f"[DEBUG] {DATA_FILE} not found or is empty/invalid JSON. Initializing with new data.")
                        with open(DATA_FILE, 'w', encoding='utf-8') as f:
                            json.dump([latest_data], f, indent=4)
            time.sleep(0.05)
        except (serial.SerialException, TypeError, UnicodeDecodeError) as e:
            with data_lock:
                raw_serial_log.append(f"[ERROR] {e}")
            stop_thread = True
            break
    print("Thread pembacaan serial dihentikan.")

# --- Rute-rute Aplikasi Flask ---

@app.route('/')
def index():
    return redirect(url_for('admin_login') if not ser or not ser.is_open else url_for('dashboard_page'))

@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if 'admin_logged_in' in session: return redirect(url_for('admin_dashboard'))
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        try:
            with open(USER_FILE, 'r', encoding='utf-8') as f:
                users = json.load(f)
            
            user_found = False
            for user in users:
                if user.get('username') == username and user.get('password') == password:
                    session['admin_logged_in'] = True
                    session['username'] = username
                    user_found = True
                    break
            
            if user_found:
                return redirect(url_for('admin_config'))
            else:
                error = "Username atau password salah."

        except (FileNotFoundError, json.JSONDecodeError):
            error = "File database pengguna tidak ditemukan atau rusak."

    return render_template('admin_login.html', error=error)

@app.route('/admin/config', methods=['GET', 'POST'])
def admin_config():
    if 'admin_logged_in' not in session: return redirect(url_for('admin_login'))
    global ser
    if ser and ser.is_open:
        return redirect(url_for('admin_dashboard'))
    global serial_thread, stop_thread, current_port, current_baudrate
    if request.method == 'POST':
        port, baudrate = request.form.get('port'), int(request.form.get('baudrate'))
        if ser and ser.is_open: stop_thread, ser.close(), serial_thread.join() if serial_thread else None
        try:
            ser = serial.Serial(port, baudrate, timeout=1)
            current_port, current_baudrate = port, baudrate
            stop_thread = False
            serial_thread = threading.Thread(target=read_from_port, daemon=True).start()
            return redirect(url_for('admin_dashboard'))
        except serial.SerialException as e:
            return render_template('admin_config.html', ports=serial.tools.list_ports.comports(), error=str(e))
    return render_template('admin_config.html', ports=serial.tools.list_ports.comports())

@app.route('/admin/dashboard')
def admin_dashboard():
    if 'admin_logged_in' not in session: return redirect(url_for('admin_login'))
    if not ser or not ser.is_open: return redirect(url_for('admin_config'))
    return render_template('admin_dashboard.html', port=current_port, baudrate=current_baudrate)

@app.route('/admin/logout')
def admin_logout():
    session.clear()
    return redirect(url_for('admin_login'))

@app.route('/dashboard')
def dashboard_page():
    return render_template('dashboard.html')

@app.route('/documentation')
def documentation_page():
    return render_template('documentation.html')

@app.route('/about')
def about_page():
    return render_template('about.html')

@app.route('/api-docs')
def api_docs_page():
    return render_template('api_info.html')

# --- Rute API dan Fungsi Statistik ---

def calculate_statistics():
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f: records = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError): return {}
    
    daily_aggregates = {}
    keys_to_track = ['ph', 'pollution', 'celsius', 'water_level']

    for record in records:
        try:
            day_str = datetime.strptime(record['timestamp'], '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d')
            converted = record.get('converted', {})
        except (ValueError, TypeError): continue

        if day_str not in daily_aggregates:
            daily_aggregates[day_str] = {
                'sums': {k: 0 for k in keys_to_track},
                'mins': {k: float('inf') for k in keys_to_track},
                'maxs': {k: float('-inf') for k in keys_to_track},
                'count': 0
            }
        
        agg = daily_aggregates[day_str]
        agg['count'] += 1
        for key in keys_to_track:
            value = converted.get(key, 0)
            agg['sums'][key] += value
            if value < agg['mins'][key]: agg['mins'][key] = value
            if value > agg['maxs'][key]: agg['maxs'][key] = value

    final_stats = {}
    for day, agg in daily_aggregates.items():
        count = agg['count']
        final_stats[day] = {
            'averages': {k: round(agg['sums'][k] / count, 1) for k in keys_to_track},
            'lows': {k: agg['mins'][k] if agg['mins'][k] != float('inf') else 0 for k in keys_to_track},
            'highs': {k: agg['maxs'][k] if agg['maxs'][k] != float('-inf') else 0 for k in keys_to_track}
        }
    return final_stats

@app.route('/api/monitoring')
def get_monitoring_data():
    with data_lock: data_copy = latest_data.copy()
    data_copy['connection'] = {'port': current_port, 'baudrate': current_baudrate}
    return jsonify(data_copy)

@app.route('/api/statistics')
def get_statistics():
    return jsonify(calculate_statistics())

@app.route('/serial_log')
def get_serial_log():
    with data_lock: return jsonify(list(raw_serial_log))

@app.route('/control', methods=['POST'])
def control_device():
    if 'admin_logged_in' not in session: return jsonify({"status": "error", "message": "Akses ditolak"}), 403
    if not ser or not ser.is_open: return jsonify({"status": "error", "message": "Port serial tidak terhubung"}), 500
    command = '1' if request.get_json().get('state') == 'on' else '0'
    try:
        ser.write(command.encode('utf-8'))
        return jsonify({"status": "sukses"})
    except serial.SerialException as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/admin/send_command', methods=['POST'])
def send_admin_command():
    if 'admin_logged_in' not in session: 
        return jsonify({"status": "error", "message": "Akses ditolak"}), 403
    if not ser or not ser.is_open: 
        return jsonify({"status": "error", "message": "Port serial tidak terhubung"}), 500
    
    data = request.get_json()
    command = data.get('command')

    if not command or command not in ['1', '2', '3', '4', '5', '6', '7']:
        return jsonify({"status": "error", "message": "Perintah tidak valid"}), 400

    try:
        ser.write(command.encode('utf-8'))
        return jsonify({"status": "sukses", "command_sent": command})
    except serial.SerialException as e:
        return jsonify({"status": "error", "message": str(e)}), 500




# --- Menjalankan Aplikasi ---
if __name__ == '__main__':
    app.run(debug=True, threaded=True, use_reloader=False)
