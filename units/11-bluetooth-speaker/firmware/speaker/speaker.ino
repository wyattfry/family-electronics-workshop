// Unit 11: Bluetooth speaker firmware for an ORIGINAL ESP32 (WROOM-32).
// ESP32-S3/C3/C6 do NOT support Bluetooth Classic A2DP.
//
// Libraries (Arduino Library Manager or GitHub, both by Phil Schatzmann):
//   - ESP32-A2DP          https://github.com/pschatzmann/ESP32-A2DP
//   - arduino-audio-tools https://github.com/pschatzmann/arduino-audio-tools
// The API has changed between major versions; if this doesn't compile, compare
// with the library's current README example ("A2DP sink with I2S").
//
// Wiring (both MAX98357A amps share the same three I2S lines):
//   ESP32 GPIO26 -> BCLK
//   ESP32 GPIO25 -> LRC (word select)
//   ESP32 GPIO22 -> DIN
//   5V / GND     -> Vin / GND
//   Left amp:  SD tied to Vin.   Right amp: 470k from SD to Vin.  (see README)

#include "AudioTools.h"
#include "BluetoothA2DPSink.h"

const char *SPEAKER_NAME = "Workshop Speaker";  // what shows up on your phone -- name it!

I2SStream i2s;
BluetoothA2DPSink a2dp_sink(i2s);

void setup() {
  Serial.begin(115200);

  auto cfg = i2s.defaultConfig();
  cfg.pin_bck = 26;
  cfg.pin_ws = 25;
  cfg.pin_data = 22;
  i2s.begin(cfg);

  a2dp_sink.start(SPEAKER_NAME);
  Serial.println("Ready to pair!");
}

void loop() {
  delay(1000);  // all the work happens in the Bluetooth callbacks
}
