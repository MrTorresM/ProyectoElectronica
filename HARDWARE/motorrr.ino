#include <Arduino.h>
#include <TM1637Display.h>

// ===========================================================
// =============== CONFIGURACIÓN DE PINES ====================
// Motor 1
#define M1_IN1 5
#define M1_IN2 4
#define M1_IN3 3
#define M1_IN4 2

// Motor 2 (usando pines analógicos como digitales)
#define M2_IN1 A5
#define M2_IN2 A4
#define M2_IN3 A3
#define M2_IN4 A2

// Botones
#define BTN1_IZQ 13
#define BTN1_DER 12
#define BTN2_IZQ 9
#define BTN2_DER 8

// Displays
#define CLK1 11
#define DIO1 10
#define CLK2 7
#define DIO2 6

// ===========================================================
// Variables globales
int demora = 20;
int contador1 = 90;
int contador2 = 90;

TM1637Display display1(CLK1, DIO1);
TM1637Display display2(CLK2, DIO2);

// ===========================================================
void setup() {
  // ---- Motores ----
  pinMode(M1_IN1, OUTPUT);
  pinMode(M1_IN2, OUTPUT);
  pinMode(M1_IN3, OUTPUT);
  pinMode(M1_IN4, OUTPUT);

  pinMode(M2_IN1, OUTPUT);
  pinMode(M2_IN2, OUTPUT);
  pinMode(M2_IN3, OUTPUT);
  pinMode(M2_IN4, OUTPUT);

  // ---- Botones ----
  pinMode(BTN1_DER, INPUT_PULLUP);
  pinMode(BTN1_IZQ, INPUT_PULLUP);
  pinMode(BTN2_DER, INPUT_PULLUP);
  pinMode(BTN2_IZQ, INPUT_PULLUP);

  // ---- Displays ----
  display1.setBrightness(0x0f);
  display1.showNumberDec(contador1);

  display2.setBrightness(0x0f);
  display2.showNumberDec(contador2);
}

// ===========================================================
// Funciones de movimiento para motor 1
void motor1Derecha() {
  for (int i = 0; i < 6; i++) {
    digitalWrite(M1_IN1, LOW);
    digitalWrite(M1_IN2, LOW);
    digitalWrite(M1_IN3, LOW);
    digitalWrite(M1_IN4, HIGH);
    delay(demora);

    digitalWrite(M1_IN1, LOW);
    digitalWrite(M1_IN2, LOW);
    digitalWrite(M1_IN3, HIGH);
    digitalWrite(M1_IN4, LOW);
    delay(demora);

    digitalWrite(M1_IN1, LOW);
    digitalWrite(M1_IN2, HIGH);
    digitalWrite(M1_IN3, LOW);
    digitalWrite(M1_IN4, LOW);
    delay(demora);

    digitalWrite(M1_IN1, HIGH);
    digitalWrite(M1_IN2, LOW);
    digitalWrite(M1_IN3, LOW);
    digitalWrite(M1_IN4, LOW);
    delay(demora);
  }
  digitalWrite(M1_IN1, LOW);
  digitalWrite(M1_IN2, LOW);
  digitalWrite(M1_IN3, LOW);
  digitalWrite(M1_IN4, LOW);
}

void motor1Izquierda() {
  for (int i = 0; i < 6; i++) {
    digitalWrite(M1_IN1, HIGH);
    digitalWrite(M1_IN2, LOW);
    digitalWrite(M1_IN3, LOW);
    digitalWrite(M1_IN4, LOW);
    delay(demora);

    digitalWrite(M1_IN1, LOW);
    digitalWrite(M1_IN2, HIGH);
    digitalWrite(M1_IN3, LOW);
    digitalWrite(M1_IN4, LOW);
    delay(demora);

    digitalWrite(M1_IN1, LOW);
    digitalWrite(M1_IN2, LOW);
    digitalWrite(M1_IN3, HIGH);
    digitalWrite(M1_IN4, LOW);
    delay(demora);

    digitalWrite(M1_IN1, LOW);
    digitalWrite(M1_IN2, LOW);
    digitalWrite(M1_IN3, LOW);
    digitalWrite(M1_IN4, HIGH);
    delay(demora);
  }
  digitalWrite(M1_IN1, LOW);
  digitalWrite(M1_IN2, LOW);
  digitalWrite(M1_IN3, LOW);
  digitalWrite(M1_IN4, LOW);
}

// ===========================================================
// Funciones de movimiento para motor 2
void motor2Derecha() {
  for (int i = 0; i < 6; i++) {
    digitalWrite(M2_IN1, LOW);
    digitalWrite(M2_IN2, LOW);
    digitalWrite(M2_IN3, LOW);
    digitalWrite(M2_IN4, HIGH);
    delay(demora);

    digitalWrite(M2_IN1, LOW);
    digitalWrite(M2_IN2, LOW);
    digitalWrite(M2_IN3, HIGH);
    digitalWrite(M2_IN4, LOW);
    delay(demora);

    digitalWrite(M2_IN1, LOW);
    digitalWrite(M2_IN2, HIGH);
    digitalWrite(M2_IN3, LOW);
    digitalWrite(M2_IN4, LOW);
    delay(demora);

    digitalWrite(M2_IN1, HIGH);
    digitalWrite(M2_IN2, LOW);
    digitalWrite(M2_IN3, LOW);
    digitalWrite(M2_IN4, LOW);
    delay(demora);
  }
  digitalWrite(M2_IN1, LOW);
  digitalWrite(M2_IN2, LOW);
  digitalWrite(M2_IN3, LOW);
  digitalWrite(M2_IN4, LOW);
}

void motor2Izquierda() {
  for (int i = 0; i < 6; i++) {
    digitalWrite(M2_IN1, HIGH);
    digitalWrite(M2_IN2, LOW);
    digitalWrite(M2_IN3, LOW);
    digitalWrite(M2_IN4, LOW);
    delay(demora);

    digitalWrite(M2_IN1, LOW);
    digitalWrite(M2_IN2, HIGH);
    digitalWrite(M2_IN3, LOW);
    digitalWrite(M2_IN4, LOW);
    delay(demora);

    digitalWrite(M2_IN1, LOW);
    digitalWrite(M2_IN2, LOW);
    digitalWrite(M2_IN3, HIGH);
    digitalWrite(M2_IN4, LOW);
    delay(demora);

    digitalWrite(M2_IN1, LOW);
    digitalWrite(M2_IN2, LOW);
    digitalWrite(M2_IN3, LOW);
    digitalWrite(M2_IN4, HIGH);
    delay(demora);
  }
  digitalWrite(M2_IN1, LOW);
  digitalWrite(M2_IN2, LOW);
  digitalWrite(M2_IN3, LOW);
  digitalWrite(M2_IN4, LOW);
}

// ===========================================================
// Bucle principal
void loop() {
  // --- Motor / Display 1 ---
  if (digitalRead(BTN1_DER) == LOW) {
    delay(50);
    if (digitalRead(BTN1_DER) == LOW) {
      contador1++;
      if (contador1 > 9999) contador1 = 9999;
      display1.showNumberDec(contador1);
      motor1Derecha();
      delay(200);
    }
  }

  if (digitalRead(BTN1_IZQ) == LOW) {
    delay(50);
    if (digitalRead(BTN1_IZQ) == LOW) {
      contador1--;
      if (contador1 < 0) contador1 = 0;
      display1.showNumberDec(contador1);
      motor1Izquierda();
      delay(200);
    }
  }

  // --- Motor / Display 2 ---
  if (digitalRead(BTN2_DER) == LOW) {
    delay(50);
    if (digitalRead(BTN2_DER) == LOW) {
      contador2++;
      if (contador2 > 9999) contador2 = 9999;
      display2.showNumberDec(contador2);
      motor2Derecha();
      delay(200);
    }
  }

  if (digitalRead(BTN2_IZQ) == LOW) {
    delay(50);
    if (digitalRead(BTN2_IZQ) == LOW) {
      contador2--;
      if (contador2 < 0) contador2 = 0;
      display2.showNumberDec(contador2);
      motor2Izquierda();
      delay(200);
    }
  }
}
