// Unit 16: handheld controller for the micro RC cars.
// Board: any classic ESP32 devkit (ESP32-WROOM-32). Arduino core: esp32 3.x.
// Libraries: Adafruit SSD1306 + Adafruit GFX.
//
// Wiring:
//   Left stick  Y (throttle) -> GPIO34     Right stick X (steering) -> GPIO35
//   Joystick modules powered from 3V3 (NOT 5V: the ESP32 ADC tops out at 3.3 V)
//   Buttons to GND: MODE -> GPIO25, LIGHTS -> GPIO26, CAR# -> GPIO27
//   SSD1306 128x64 OLED: SDA -> GPIO21, SCL -> GPIO22, VCC -> 3V3
//
// Joysticks MUST be on ADC1 pins (GPIO32-39). ADC2 doesn't work while the
// radio is on, and ESP-NOW uses the radio.

#include <WiFi.h>
#include <esp_now.h>
#include <esp_wifi.h>
#include <Preferences.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include "protocol.h"

const int PIN_THROTTLE = 34, PIN_STEER = 35;
const int PIN_BTN_MODE = 25, PIN_BTN_LIGHTS = 26, PIN_BTN_CAR = 27;
const int MAX_CARS = 4;
const int DEADBAND = 8;          // % of stick travel ignored around center
const bool INVERT_THROTTLE = false, INVERT_STEER = false;

Adafruit_SSD1306 oled(128, 64, &Wire, -1);
Preferences prefs;
const uint8_t BROADCAST[6] = {0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF};

uint8_t carId = 1;
uint8_t mode = MODE_MANUAL;
bool lightsOn = true;
int centerThrottle = 2048, centerSteer = 2048;

portMUX_TYPE rxLock = portMUX_INITIALIZER_UNLOCKED;
TelemetryPacket telem = {};
uint32_t telemMs = 0;

#if ESP_ARDUINO_VERSION_MAJOR >= 3
void onReceive(const esp_now_recv_info_t *info, const uint8_t *data, int len) {
#else
void onReceive(const uint8_t *mac, const uint8_t *data, int len) {
#endif
  if (len != sizeof(TelemetryPacket)) return;
  TelemetryPacket t;
  memcpy(&t, data, sizeof t);
  if (t.magic != PROTO_MAGIC || t.type != MSG_TELEMETRY || t.carId != carId) return;
  portENTER_CRITICAL(&rxLock);
  telem = t;
  telemMs = millis();
  portEXIT_CRITICAL(&rxLock);
}

// Stick reading -> -100..100, with a center deadband.
int stick(int pin, int center, bool invert) {
  int raw = analogRead(pin);
  int v = raw >= center ? map(raw, center, 4095, 0, 100) : map(raw, 0, center, -100, 0);
  if (abs(v) < DEADBAND) v = 0;
  v = constrain(v, -100, 100);
  return invert ? -v : v;
}

// True once per press (simple debounce).
bool pressed(int pin) {
  static uint32_t lastMs[40] = {};
  static bool lastDown[40] = {};
  bool down = digitalRead(pin) == LOW;
  bool fired = down && !lastDown[pin] && millis() - lastMs[pin] > 150;
  if (down != lastDown[pin]) lastMs[pin] = millis();
  lastDown[pin] = down;
  return fired;
}

const char *modeName(uint8_t m) {
  switch (m) {
    case MODE_MANUAL: return "DRIVE";
    case MODE_AVOID: return "SAFE";
    case MODE_AUTO: return "ROBOT";
    case MODE_BRAIN: return "BRAIN";
  }
  return "?";
}

void draw(int throttle, int steer) {
  TelemetryPacket t;
  uint32_t tMs;
  portENTER_CRITICAL(&rxLock);
  t = telem;
  tMs = telemMs;
  portEXIT_CRITICAL(&rxLock);
  bool fresh = tMs && millis() - tMs < 1000;

  oled.clearDisplay();
  oled.setTextColor(SSD1306_WHITE);
  oled.setTextSize(2);
  oled.setCursor(0, 0);
  oled.printf("CAR %d", carId);
  oled.setCursor(76, 0);
  oled.print(modeName(mode));
  oled.setTextSize(1);
  oled.setCursor(0, 22);
  if (!fresh) {
    oled.print("no signal from car");
  } else {
    oled.printf("batt %3d%% %s", t.batteryPct, t.charging ? "CHARGING" : "");
    oled.setCursor(0, 34);
    if (t.distanceMm == DISTANCE_NONE) oled.print("dist  --");
    else oled.printf("dist %4d mm", t.distanceMm);
    oled.drawRect(0, 46, 102, 6, SSD1306_WHITE);  // battery bar
    oled.fillRect(1, 47, t.batteryPct, 4, SSD1306_WHITE);
  }
  oled.setCursor(0, 56);
  oled.printf("thr %4d  str %4d %s", throttle, steer, lightsOn ? "*" : " ");
  oled.display();
}

void setup() {
  Serial.begin(115200);
  pinMode(PIN_BTN_MODE, INPUT_PULLUP);
  pinMode(PIN_BTN_LIGHTS, INPUT_PULLUP);
  pinMode(PIN_BTN_CAR, INPUT_PULLUP);
  analogReadResolution(12);

  prefs.begin("rc", false);
  carId = prefs.getUChar("car", 1);

  // Calibrate stick centers: don't touch the sticks while it powers on!
  long a = 0, b = 0;
  for (int i = 0; i < 32; i++) { a += analogRead(PIN_THROTTLE); b += analogRead(PIN_STEER); delay(2); }
  centerThrottle = a / 32;
  centerSteer = b / 32;

  Wire.begin(21, 22);
  if (!oled.begin(SSD1306_SWITCHCAPVCC, 0x3C)) Serial.println("OLED not found");

  WiFi.mode(WIFI_STA);
  esp_wifi_set_channel(WIFI_CHANNEL, WIFI_SECOND_CHAN_NONE);
  esp_now_init();
  esp_now_register_recv_cb(onReceive);
  esp_now_peer_info_t peer = {};
  memcpy(peer.peer_addr, BROADCAST, 6);
  peer.channel = WIFI_CHANNEL;
  esp_now_add_peer(&peer);
}

void loop() {
  static uint8_t seq = 0;
  static uint32_t lastDraw = 0;

  if (pressed(PIN_BTN_MODE)) mode = (mode + 1) % MODE_COUNT;
  if (pressed(PIN_BTN_LIGHTS)) lightsOn = !lightsOn;
  if (pressed(PIN_BTN_CAR)) {
    carId = carId % MAX_CARS + 1;
    prefs.putUChar("car", carId);
    mode = MODE_MANUAL;  // never hand a different car an active ROBOT mode
  }

  int throttle = stick(PIN_THROTTLE, centerThrottle, INVERT_THROTTLE);
  int steer = stick(PIN_STEER, centerSteer, INVERT_STEER);

  ControlPacket p = {PROTO_MAGIC, MSG_CONTROL, carId, (int8_t)throttle, (int8_t)steer,
                     mode, (uint8_t)(lightsOn ? FLAG_LIGHTS : 0), seq++};
  esp_now_send(BROADCAST, (const uint8_t *)&p, sizeof p);

  if (millis() - lastDraw > 100) { lastDraw = millis(); draw(throttle, steer); }
  delay(20);  // ~50 packets a second
}
