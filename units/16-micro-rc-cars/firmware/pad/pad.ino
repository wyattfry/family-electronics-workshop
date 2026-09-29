// Unit 16: charging pad "fuel gauge".
// Listens for car telemetry. When a car reports it's charging, a WS2812 ring
// shows its battery level; otherwise the ring "breathes" slowly so you can
// find the pad in the dark.
// Board: any ESP32 (an ESP32-C3 SuperMini is tiny and cheap). Core: esp32 3.x.
// Library: Adafruit NeoPixel.
// Wiring: ring DIN -> GPIO 4 (through a 330 ohm resistor), 5V, GND. Power from the
// same USB supply as the Qi pad.

#include <WiFi.h>
#include <esp_now.h>
#include <esp_wifi.h>
#include <Adafruit_NeoPixel.h>
#include "protocol.h"

const int PIN_RING = 4;
const int RING_LEDS = 12;
Adafruit_NeoPixel ring(RING_LEDS, PIN_RING, NEO_GRB + NEO_KHZ800);

portMUX_TYPE rxLock = portMUX_INITIALIZER_UNLOCKED;
TelemetryPacket car = {};
uint32_t carMs = 0;

#if ESP_ARDUINO_VERSION_MAJOR >= 3
void onReceive(const esp_now_recv_info_t *info, const uint8_t *data, int len) {
#else
void onReceive(const uint8_t *mac, const uint8_t *data, int len) {
#endif
  if (len != sizeof(TelemetryPacket)) return;
  TelemetryPacket t;
  memcpy(&t, data, sizeof t);
  if (t.magic != PROTO_MAGIC || t.type != MSG_TELEMETRY || !t.charging) return;
  portENTER_CRITICAL(&rxLock);
  car = t;
  carMs = millis();
  portEXIT_CRITICAL(&rxLock);
}

uint32_t levelColor(uint8_t pct) {  // red -> yellow -> green
  if (pct < 50) return ring.Color(60, pct * 60 / 50, 0);
  return ring.Color((100 - pct) * 60 / 50, 60, 0);
}

void setup() {
  ring.begin();
  ring.clear();
  ring.show();
  WiFi.mode(WIFI_STA);
  esp_wifi_set_channel(WIFI_CHANNEL, WIFI_SECOND_CHAN_NONE);
  esp_now_init();
  esp_now_register_recv_cb(onReceive);
}

void loop() {
  TelemetryPacket t;
  uint32_t tMs;
  portENTER_CRITICAL(&rxLock);
  t = car;
  tMs = carMs;
  portEXIT_CRITICAL(&rxLock);

  ring.clear();
  if (tMs && millis() - tMs < 1500) {
    // A car is charging: fill the ring to its battery %, with the next LED pulsing.
    int lit = t.batteryPct * RING_LEDS / 100;
    for (int i = 0; i < lit; i++) ring.setPixelColor(i, levelColor(t.batteryPct));
    if (lit < RING_LEDS && (millis() / 400) % 2) ring.setPixelColor(lit, levelColor(t.batteryPct));
    if (t.batteryPct >= 100) for (int i = 0; i < RING_LEDS; i++) ring.setPixelColor(i, ring.Color(0, 60, 0));
  } else {
    // Idle: slow blue breathing.
    float phase = (millis() % 4000) / 4000.0f;
    uint8_t b = 5 + 25 * (0.5f - 0.5f * cosf(phase * 2 * PI));
    for (int i = 0; i < RING_LEDS; i++) ring.setPixelColor(i, ring.Color(0, 0, b));
  }
  ring.show();
  delay(30);
}
