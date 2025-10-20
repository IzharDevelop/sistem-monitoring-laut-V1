// === PENGATURAN PIN ===
// Sensor
const int SUHU_PIN = A5;
const int UDARA_PIN = A4;
const int WATER_PIN = A3;
const int TDS_PIN = A2;
const int GYRO_KIRI_PIN = A1;
const int GYRO_KANAN_PIN = A0;

// Aktuator (LED & Buzzer)
const int LED_HIJAU_PIN = 7;
const int LED_MERAH_PIN = 10;
const int LED_KONVEYOR_PIN = 8;
const int LED_KIRI_PIN = 13;
const int LED_KANAN_PIN = 12; // Asumsi pin 12 untuk giro kanan, karena tidak disebutkan.
const int BUZZER_PIN = 11; z

// === VARIABEL GLOBAL ===
// Variabel untuk menyimpan nilai dari sensor
int nilaiTds = 0;
int nilaiGiroKanan = 0;
int nilaiGiroKiri = 0;
int nilaiUdara = 0;
int nilaiSuhu = 0;
int nilaiAir = 0;

// Variabel untuk status (digunakan untuk pencetakan serial)
int statusKonveyor = 0; // 0 = Mati, 1 = Nyala
// ------------------------------------

void setup() {
  // Memulai komunikasi serial pada 9600 bps
  Serial.begin(9600);

  // Mengatur mode pin untuk aktuator sebagai OUTPUT
  pinMode(LED_HIJAU_PIN, OUTPUT);
  pinMode(LED_MERAH_PIN, OUTPUT);
  pinMode(LED_KONVEYOR_PIN, OUTPUT);
  pinMode(LED_KIRI_PIN, OUTPUT);
  pinMode(LED_KANAN_PIN, OUTPUT);
  pinMode(BUZZER_PIN, OUTPUT);

  // Mengatur mode pin untuk sensor sebagai INPUT
  pinMode(TDS_PIN, INPUT);
  pinMode(GYRO_KANAN_PIN, INPUT);
  pinMode(GYRO_KIRI_PIN, INPUT);

  // Kondisi awal: LED hijau menyala, yang lain mati
  digitalWrite(LED_HIJAU_PIN, HIGH);
  digitalWrite(LED_MERAH_PIN, LOW);
  digitalWrite(LED_KONVEYOR_PIN, LOW);
  digitalWrite(LED_KIRI_PIN, LOW);
  digitalWrite(LED_KANAN_PIN, LOW);
  noTone(BUZZER_PIN);
}

void loop() {
  // 1. BACA SEMUA NILAI SENSOR
  nilaiTds = analogRead(TDS_PIN);
  nilaiGiroKanan = analogRead(GYRO_KANAN_PIN);
  nilaiGiroKiri = analogRead(GYRO_KIRI_PIN);
  nilaiUdara = analogRead(UDARA_PIN);
  nilaiSuhu = analogRead(SUHU_PIN);
  nilaiAir = analogRead(WATER_PIN);

  // 2. PROSES PERINTAH DARI SERIAL MONITOR
  if (Serial.available() > 0) {
    char command = Serial.read();
    if (command == '1') {
      digitalWrite(LED_KONVEYOR_PIN, HIGH);
      statusKonveyor = 1;
    } else if (command == '0') {
      digitalWrite(LED_KONVEYOR_PIN, LOW);
      statusKonveyor = 0;
    }
  }

  // 3. LOGIKA SENSOR TDS (KUALITAS AIR)
  if (nilaiTds > 450) {
    // Kualitas air buruk
    digitalWrite(LED_MERAH_PIN, HIGH);
    digitalWrite(LED_HIJAU_PIN, LOW);
    bunyikanBuzzer(); // Peringatan bep bep bep
  } else {
    // Kualitas air baik
    digitalWrite(LED_MERAH_PIN, LOW);
    digitalWrite(LED_HIJAU_PIN, HIGH);
    noTone(BUZZER_PIN); // Pastikan buzzer mati
  }

  // 4. LOGIKA SENSOR GIRO KANAN
  if (nilaiGiroKanan > 100) {
    digitalWrite(LED_KANAN_PIN, HIGH);
  } else {
    digitalWrite(LED_KANAN_PIN, LOW);
  }

  // 5. LOGIKA SENSOR GIRO KIRI
  if (nilaiGiroKiri > 100) {
    digitalWrite(LED_KIRI_PIN, HIGH);
  } else {
    digitalWrite(LED_KIRI_PIN, LOW);
  }

  // 6. KIRIM SEMUA DATA KE SERIAL MONITOR
  cetakStatusKeSerial();

  // Beri jeda 1 detik sebelum loop berikutnya
  delay(1000);
}

// Fungsi untuk membunyikan buzzer dengan pola bep-bep-bep
void bunyikanBuzzer() {
  tone(BUZZER_PIN, 1000, 100); // Nada 1000Hz selama 100ms
  delay(150);
  tone(BUZZER_PIN, 1000, 100);
  delay(150);
  tone(BUZZER_PIN, 1000, 100);
}

// Fungsi untuk mencetak semua status ke Serial Monitor
void cetakStatusKeSerial() {
  // Urutan: [Nilai_pH],[Nilai_TDS],[Nilai_Suhu],[Giro_Kanan],[Giro_Kiri],[Level_Air],[Status_Konveyor]
  Serial.print(nilaiTds); // nilai ph air
  Serial.print(",");
  Serial.print(nilaiUdara); // nilai udara 
  Serial.print(",");
  Serial.print(nilaiSuhu); // Nilai suhu
  Serial.print(",");
  Serial.print(nilaiGiroKanan); // Nilai Gyro kanan
  Serial.print(",");
  Serial.print(nilaiGiroKiri); // nilai gyro kiri
  Serial.print(",");
  Serial.print(nilaiAir); // nilai air
  Serial.print(",");
  Serial.println(statusKonveyor); // Logic
}
