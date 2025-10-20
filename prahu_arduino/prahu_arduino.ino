// Deklarasi pin motor A pada modul L9110S
// Ganti nomor pin ini jika Anda menggunakan pin yang berbeda
const int MotorA_IA = 9;  // Pin A-IA (harus pin PWM)
const int MotorA_IB = 10; // Pin A-IB (harus pin PWM)

// Variabel untuk menyimpan input dari Serial Monitor
int inputNilai = 0;
int kecepatanMotor = 0;

void setup() {
  // Set pin motor sebagai OUTPUT
  pinMode(MotorA_IA, OUTPUT);
  pinMode(MotorA_IB, OUTPUT);
  
  // Inisialisasi komunikasi serial
  Serial.begin(9600);
  Serial.println("--- KONTROL MOTOR DC L9110S ---");
  Serial.println("Masukkan nilai di Serial Monitor:");
  Serial.println("0: Berhenti");
  Serial.println("1 - 255: Maju (kecepatan)");
  Serial.println("-1 - -255: Mundur (kecepatan)");
}

void loop() {
  // Cek apakah ada data yang masuk melalui Serial Monitor
  if (Serial.available() > 0) {
    // Baca input sebagai bilangan bulat
    inputNilai = Serial.parseInt();
    
    // Pastikan tidak ada karakter yang tersisa di buffer serial
    while (Serial.available()) {
      Serial.read();
    }
    
    // Batasi nilai input antara -255 dan 255
    if (inputNilai > 255) {
      inputNilai = 255;
    } else if (inputNilai < -255) {
      inputNilai = -255;
    }

    // --- LOGIKA KONTROL MOTOR ---

    if (inputNilai == 0) {
      // Perintah 1: BERHENTI
      berhentiMotor();
      Serial.println("Perintah: BERHENTI");
      
    } else if (inputNilai > 0) {
      // Perintah 2: MAJU (nilai positif 1 hingga 255)
      kecepatanMotor = inputNilai;
      majuMotor(kecepatanMotor);
      Serial.print("Perintah: MAJU, Kecepatan: ");
      Serial.println(kecepatanMotor);
      
    } else { // inputNilai < 0
      // Perintah 3: MUNDUR (nilai negatif -1 hingga -255)
      // Ambil nilai absolut (misal: -100 menjadi 100)
      kecepatanMotor = abs(inputNilai); 
      mundurMotor(kecepatanMotor);
      Serial.print("Perintah: MUNDUR, Kecepatan: ");
      Serial.println(kecepatanMotor);
    }
  }
}

// --- FUNGSI KONTROL MOTOR ---

void majuMotor(int speed) {
  // Motor Maju: A-IA = Kecepatan (PWM), A-IB = LOW (0)
  analogWrite(MotorA_IA, speed);
  analogWrite(MotorA_IB, 0);
}

void mundurMotor(int speed) {
  // Motor Mundur: A-IA = LOW (0), A-IB = Kecepatan (PWM)
  analogWrite(MotorA_IA, 0);
  analogWrite(MotorA_IB, speed);
}

void berhentiMotor() {
  // Berhenti (Pengereman)
  analogWrite(MotorA_IA, 0);
  analogWrite(MotorA_IB, 0);
}