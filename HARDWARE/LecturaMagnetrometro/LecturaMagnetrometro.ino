#include <Wire.h>
#include <ArduinoJson.h>

// ===== Configuración Magnetómetro HMC5883L =====
#define HMC_ADDR      0x1E
#define REG_CONF_A    0x00
#define REG_CONF_B    0x01
#define REG_MODE      0x02
#define REG_OUT_X_MSB 0x03

// Declination: Bogotá ≈ -8.33°
const float DECLINATION_ANGLE = -8.33f;

int16_t rawX, rawY, rawZ;
int16_t minX = 32767, maxX = -32768;
int16_t minY = 32767, maxY = -32768;
float offsetX = 0, offsetY = 0;

unsigned long lastSend = 0;
const unsigned long SEND_INTERVAL = 200;  // cada 200 ms

// ======== Methods Definition ========
void readRawMag();
float getHeadingDegrees(float x, float y);

void setup() {
  Serial.begin(115200);
  delay(500);
  Serial.println("\n=== Iniciando Lectura del Magnetómetro HMC5883L ===");

  // Inicializar I2C
  Wire.begin(21, 22);
  Wire.setClock(400000UL);

  // Configurar el HMC5883L
  Wire.beginTransmission(HMC_ADDR);
  Wire.write(REG_CONF_A); Wire.write(0x70);  // 8 samples @15Hz
  Wire.endTransmission();
  Wire.beginTransmission(HMC_ADDR);
  Wire.write(REG_CONF_B); Wire.write(0xA0);  // ±5.6 Gauss
  Wire.endTransmission();

  // ===== Calibración (10 s) =====
  Serial.println("> Calibración: gira el módulo 360° durante 10 segundos...");
  unsigned long start = millis();
  while (millis() - start < 10000) {
    readRawMag();
    minX = min(minX, rawX); maxX = max(maxX, rawX);
    minY = min(minY, rawY); maxY = max(maxY, rawY);
    delay(100);
  }
  offsetX = (maxX + minX) / 2.0f;
  offsetY = (maxY + minY) / 2.0f;
  Serial.printf("> Calibración completa. Offsets: X=%.1f, Y=%.1f\n", offsetX, offsetY);
  Serial.println("=== Lectura continua iniciada ===\n");
}

void loop() {
  if (millis() - lastSend >= SEND_INTERVAL) {
    lastSend = millis();

    // Leer ejes crudos
    readRawMag();
    float x = rawX - offsetX;
    float y = rawY - offsetY;
    float heading = getHeadingDegrees(x, y);

    // Crear JSON
    StaticJsonDocument<256> doc;
    JsonObject mag = doc.createNestedObject("magnetometro");
    mag["x_raw"] = rawX;
    mag["y_raw"] = rawY;
    mag["z_raw"] = rawZ;
    mag["heading_deg"] = heading;

    // doc["otro sensor"] = valor;

    // Serializar y enviar por puerto físico (USB)
    serializeJson(doc, Serial);
    Serial.println();
  }
}

// ====== Lectura de magnetómetro ======
void readRawMag() {
  Wire.beginTransmission(HMC_ADDR);
  Wire.write(REG_MODE);
  Wire.write(0x01);
  Wire.endTransmission();
  delay(6);

  Wire.beginTransmission(HMC_ADDR);
  Wire.write(REG_OUT_X_MSB);
  Wire.endTransmission(false);
  Wire.requestFrom(HMC_ADDR, (uint8_t)6);

  rawX = (Wire.read() << 8) | Wire.read();
  rawZ = (Wire.read() << 8) | Wire.read();
  rawY = (Wire.read() << 8) | Wire.read();

  if (rawX > 0x7FFF) rawX -= 0x10000;
  if (rawY > 0x7FFF) rawY -= 0x10000;
  if (rawZ > 0x7FFF) rawZ -= 0x10000;
}

// ====== Cálculo del ángulo en grados ======
float getHeadingDegrees(float x, float y) {
  float heading = atan2(y, x) * 180.0f / PI;
  heading += DECLINATION_ANGLE;
  if (heading < 0) heading += 360.0f;
  else if (heading >= 360.0f) heading -= 360.0f;
  return heading;
}
