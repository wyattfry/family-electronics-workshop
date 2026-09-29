// Unit 16: micro RC car firmware.
// Board: Seeed XIAO ESP32S3 (or XIAO ESP32S3 Sense for the camera stage).
// Arduino core: esp32 by Espressif, 3.x.
// Libraries: Adafruit NeoPixel; Pololu VL53L1X (only if USE_TOF is 1).
//
// See ../../README.md for the wiring, the power path, and the module ports.

#include <WiFi.h>
#include <esp_now.h>
#include <esp_wifi.h>
#include <Adafruit_NeoPixel.h>
#include "protocol.h"

// ================= CONFIG: change these for your car =================
#define CAR_ID 1          // each car in the family gets its own number
#define USE_TOF 1         // 1 = VL53L1X laser distance (I2C), 0 = RCWL-1601 ultrasonic
#define HAS_LIGHTS 1      // 0 if the light module isn't plugged in
#define HAS_BRAIN 0       // 1 = Pi Zero 2 W "brain" module on the BRAIN port (see README Part 6)

const int STEER_CENTER_US = 1500;  // trim until the car drives straight
const int STEER_RANGE_US = 350;    // how far from center full lock goes; stop before the rack binds
const bool STEER_REVERSED = false;
const bool MOTOR_REVERSED = false;
const int MAX_THROTTLE = 80;       // % cap for beginners; raise it as skills grow

const uint16_t AVOID_STOP_MM = 250;  // MODE_AVOID: refuse to drive forward closer than this
const uint16_t AUTO_TURN_MM = 400;   // MODE_AUTO: start avoiding at this distance
const int AUTO_SPEED = 45;           // MODE_AUTO cruise throttle %
const uint32_t LINK_TIMEOUT_MS = 400;  // no packets for this long = stop (failsafe)
const uint16_t LOW_BATTERY_MV = 3450;  // below this: slow down and blink
const uint16_t PI_SHUTDOWN_MV = 3500;  // brain module: ask the Pi to shut down below this
const uint32_t BRAIN_TIMEOUT_MS = 300; // brain module: no command for this long = stop
const int BRAIN_CLOSE_MAX = 25;        // brain "close approach" (docking) throttle cap, %
// =====================================================================

#if HAS_BRAIN && !USE_TOF
#error "The brain module's serial link uses the SONAR pins (D6/D7). Use the VL53L1X (USE_TOF 1)."
#endif

#if USE_TOF
#include <Wire.h>
#include <VL53L1X.h>
VL53L1X tof;
#endif

// XIAO ESP32S3 pins (the "module ports" in the README)
const int PIN_MOTOR_A = D0;   // DRV8833 AIN1
const int PIN_MOTOR_B = D1;   // DRV8833 AIN2
const int PIN_STEER = D2;     // steering servo signal
const int PIN_LIGHTS = D3;    // WS2812 data (4 LEDs: FL, FR, RL, RR)
// D4 = SDA, D5 = SCL (I2C port: distance sensor, extras)
const int PIN_TRIG = D6;      // ultrasonic TRIG (if USE_TOF is 0)
const int PIN_ECHO = D7;      // ultrasonic ECHO
const int PIN_VBAT = D8;      // battery voltage through a 100k/100k divider
const int PIN_CHARGE = D9;    // Qi 5 V through a 100k/100k divider: HIGH = on the pad
const int PIN_PI_EN = D10;    // brain module: HIGH = the Pi's 5 V boost converter is on
// Brain module serial link (only if HAS_BRAIN): XIAO D6 = TX -> Pi GPIO15 (RXD),
//                                                XIAO D7 = RX <- Pi GPIO14 (TXD)

const int SERVO_BITS = 14, SERVO_HZ = 50;
const int MOTOR_BITS = 10, MOTOR_HZ = 20000;  // 20 kHz: above hearing, no whine

Adafruit_NeoPixel lights(4, PIN_LIGHTS, NEO_GRB + NEO_KHZ800);
enum { LED_FL = 0, LED_FR = 1, LED_RL = 2, LED_RR = 3 };

// ---------- state shared with the ESP-NOW callback ----------
portMUX_TYPE rxLock = portMUX_INITIALIZER_UNLOCKED;
ControlPacket lastCmd = {};
volatile uint32_t lastCmdMs = 0;

const uint8_t BROADCAST[6] = {0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF};

// ---------- sensors ----------
uint16_t distanceMm = DISTANCE_NONE;
uint16_t batteryMv = 4000;
bool charging = false;

// ---------- outputs ----------
int currentThrottle = 0;  // what the motor is actually doing (after ramping)

#if ESP_ARDUINO_VERSION_MAJOR >= 3
void onReceive(const esp_now_recv_info_t *info, const uint8_t *data, int len) {
#else
void onReceive(const uint8_t *mac, const uint8_t *data, int len) {
#endif
  if (len != sizeof(ControlPacket)) return;
  ControlPacket p;
  memcpy(&p, data, sizeof p);
  if (p.magic != PROTO_MAGIC || p.type != MSG_CONTROL || p.carId != CAR_ID) return;
  portENTER_CRITICAL(&rxLock);
  lastCmd = p;
  lastCmdMs = millis();
  portEXIT_CRITICAL(&rxLock);
}

void setupRadio() {
  WiFi.mode(WIFI_STA);
  esp_wifi_set_channel(WIFI_CHANNEL, WIFI_SECOND_CHAN_NONE);
  if (esp_now_init() != ESP_OK) {
    Serial.println("ESP-NOW init failed");
    return;
  }
  esp_now_register_recv_cb(onReceive);
  esp_now_peer_info_t peer = {};
  memcpy(peer.peer_addr, BROADCAST, 6);
  peer.channel = WIFI_CHANNEL;
  peer.encrypt = false;
  esp_now_add_peer(&peer);
}

// ---------- actuators ----------
void setSteer(int steer) {  // -100..100
  steer = constrain(steer, -100, 100);
  if (STEER_REVERSED) steer = -steer;
  int us = STEER_CENTER_US + steer * STEER_RANGE_US / 100;
  ledcWrite(PIN_STEER, (uint32_t)us * ((1 << SERVO_BITS) - 1) / 20000);
}

void setMotor(int throttle) {  // -100..100; 0 = coast
  throttle = constrain(throttle, -100, 100);
  if (MOTOR_REVERSED) throttle = -throttle;
  uint32_t duty = (uint32_t)abs(throttle) * ((1 << MOTOR_BITS) - 1) / 100;
  if (throttle > 0) {
    ledcWrite(PIN_MOTOR_A, duty);
    ledcWrite(PIN_MOTOR_B, 0);
  } else if (throttle < 0) {
    ledcWrite(PIN_MOTOR_A, 0);
    ledcWrite(PIN_MOTOR_B, duty);
  } else {
    ledcWrite(PIN_MOTOR_A, 0);
    ledcWrite(PIN_MOTOR_B, 0);
  }
}

// Ease toward the target so the gears (and the battery) don't get slammed.
void driveToward(int target) {
  const int step = 6;  // % per 20 ms loop
  if (target > currentThrottle) currentThrottle = min(target, currentThrottle + step);
  else if (target < currentThrottle) currentThrottle = max(target, currentThrottle - step);
  setMotor(currentThrottle);
}

// ---------- sensors ----------
void readDistance() {
#if USE_TOF
  if (tof.dataReady()) {
    uint16_t mm = tof.read(false);
    distanceMm = (tof.ranging_data.range_status == VL53L1X::RangeValid) ? mm : DISTANCE_NONE;
  }
#else
  digitalWrite(PIN_TRIG, LOW);
  delayMicroseconds(2);
  digitalWrite(PIN_TRIG, HIGH);
  delayMicroseconds(10);
  digitalWrite(PIN_TRIG, LOW);
  unsigned long us = pulseIn(PIN_ECHO, HIGH, 12000);  // 12 ms ~ 2 m max
  distanceMm = us ? (uint16_t)(us * 343 / 2000) : DISTANCE_NONE;
#endif
}

uint8_t batteryPercent(uint16_t mv) {  // rough 1S LiPo curve: 3.40 V = 0 %, 4.15 V = 100 %
  return (uint8_t)constrain(map(mv, 3400, 4150, 0, 100), 0, 100);
}

void readPower() {
  batteryMv = analogReadMilliVolts(PIN_VBAT) * 2;  // undo the 100k/100k divider
  charging = digitalRead(PIN_CHARGE) == HIGH;
}

void sendTelemetry(uint8_t mode) {
  TelemetryPacket t = {PROTO_MAGIC, MSG_TELEMETRY, CAR_ID, batteryPercent(batteryMv),
                       batteryMv, distanceMm, (uint8_t)charging, mode};
  esp_now_send(BROADCAST, (const uint8_t *)&t, sizeof t);
}

// ---------- lights ----------
void showLights(bool on, int throttle, int prevThrottle, int steer, bool warn) {
#if HAS_LIGHTS
  bool blink = (millis() / 350) % 2;
  uint32_t head = on ? lights.Color(90, 90, 80) : 0;
  bool braking = throttle < 0 || (abs(throttle) < abs(prevThrottle) - 2);
  uint32_t tail = braking ? lights.Color(255, 0, 0) : (on ? lights.Color(40, 0, 0) : 0);
  uint32_t amber = lights.Color(255, 90, 0);
  lights.setPixelColor(LED_FL, head);
  lights.setPixelColor(LED_FR, head);
  lights.setPixelColor(LED_RL, tail);
  lights.setPixelColor(LED_RR, tail);
  if (steer < -60 && blink) { lights.setPixelColor(LED_FL, amber); lights.setPixelColor(LED_RL, amber); }
  if (steer > 60 && blink) { lights.setPixelColor(LED_FR, amber); lights.setPixelColor(LED_RR, amber); }
  if (warn && blink) for (int i = 0; i < 4; i++) lights.setPixelColor(i, amber);  // hazards
  lights.show();
#endif
}

void showChargeLevel() {  // on the pad: the 4 LEDs become a battery gauge
#if HAS_LIGHTS
  uint8_t pct = batteryPercent(batteryMv);
  int lit = (pct + 24) / 25;  // 1..4 LEDs
  bool pulse = (millis() / 500) % 2;
  const int order[4] = {LED_RL, LED_RR, LED_FR, LED_FL};
  for (int i = 0; i < 4; i++) {
    uint32_t c = 0;
    if (i < lit - 1 || (i == lit - 1 && (pct >= 100 || pulse))) c = lights.Color(0, 60, 0);
    lights.setPixelColor(order[i], c);
  }
  lights.show();
#endif
}

// ---------- brain module (Pi Zero 2 W) over UART ----------
// Pi -> car:  "C <throttle> <steer> <flags>\n"   at >= 10 Hz, else the car stops
// car -> Pi:  "T <battery_mv> <battery_pct> <distance_mm or -1> <charging> <mode>\n"   10 Hz
// car -> Pi:  "S\n"   battery low: please shut down now (power is cut 20 s later)
const uint8_t BRAIN_FLAG_CLOSE_OK = 1 << 1;  // docking: allow creeping up to walls, slowly
struct BrainCmd { int throttle, steer; uint8_t flags; uint32_t ms; };
BrainCmd brainCmd = {0, 0, 0, 0};
uint32_t piOffAt = 0;  // when to cut the Pi's power after asking it to shut down
int lowBatteryCount = 0;

void pollBrain() {
#if HAS_BRAIN
  static char buf[48];
  static size_t len = 0;
  while (Serial1.available()) {
    char c = Serial1.read();
    if (c == '\n') {
      buf[len] = 0;
      int t, st, f;
      if (sscanf(buf, "C %d %d %d", &t, &st, &f) == 3)
        brainCmd = {constrain(t, -100, 100), constrain(st, -100, 100), (uint8_t)f, millis()};
      len = 0;
    } else if (len < sizeof(buf) - 1) {
      buf[len++] = c;
    }
  }
#endif
}

void sendBrainTelemetry(uint8_t mode) {
#if HAS_BRAIN
  Serial1.printf("T %u %u %d %d %u\n", batteryMv, batteryPercent(batteryMv),
                 distanceMm == DISTANCE_NONE ? -1 : (int)distanceMm, (int)charging, mode);
#endif
}

// Called every 250 ms with the power readings. Pulling the plug on a running Pi can
// corrupt its SD card, so ask it to shut down first and cut power afterwards.
void managePiPower() {
#if HAS_BRAIN
  lowBatteryCount = (batteryMv < PI_SHUTDOWN_MV && !charging) ? lowBatteryCount + 1 : 0;
  if (lowBatteryCount >= 20 && piOffAt == 0) {  // 5 s of low battery, not just a motor sag
    Serial1.print("S\n");
    piOffAt = millis() + 20000;
  }
  if (piOffAt && millis() > piOffAt) digitalWrite(PIN_PI_EN, LOW);
#endif
}

// ---------- MODE_AUTO: a tiny state machine ----------
enum AutoState { CRUISE, BACKUP, TURN };
AutoState autoState = CRUISE;
uint32_t autoUntil = 0;
int autoTurnDir = 1;

void runAuto(int &throttle, int &steer) {
  uint32_t now = millis();
  switch (autoState) {
    case CRUISE:
      throttle = AUTO_SPEED;
      steer = 0;
      if (distanceMm != DISTANCE_NONE && distanceMm < AUTO_TURN_MM) {
        autoState = BACKUP;
        autoUntil = now + 700;
        autoTurnDir = -autoTurnDir;  // alternate sides so it doesn't get stuck in a corner
      }
      break;
    case BACKUP:  // reverse with the wheels turned one way...
      throttle = -AUTO_SPEED;
      steer = -100 * autoTurnDir;
      if (now > autoUntil) { autoState = TURN; autoUntil = now + 600; }
      break;
    case TURN:    // ...then go forward turned the other way: a 3-point turn
      throttle = AUTO_SPEED;
      steer = 100 * autoTurnDir;
      if (now > autoUntil) autoState = CRUISE;
      break;
  }
}

void setup() {
  Serial.begin(115200);
  ledcAttach(PIN_STEER, SERVO_HZ, SERVO_BITS);
  ledcAttach(PIN_MOTOR_A, MOTOR_HZ, MOTOR_BITS);
  ledcAttach(PIN_MOTOR_B, MOTOR_HZ, MOTOR_BITS);
  setSteer(0);
  setMotor(0);
  pinMode(PIN_CHARGE, INPUT);
  analogSetPinAttenuation(PIN_VBAT, ADC_11db);
#if USE_TOF
  Wire.begin();
  Wire.setClock(400000);
  tof.setTimeout(100);
  if (tof.init()) {
    tof.setDistanceMode(VL53L1X::Short);
    tof.setMeasurementTimingBudget(33000);
    tof.startContinuous(40);
  } else {
    Serial.println("VL53L1X not found: distance disabled");
  }
#else
  pinMode(PIN_TRIG, OUTPUT);
  pinMode(PIN_ECHO, INPUT);
#endif
#if HAS_LIGHTS
  lights.begin();
  lights.clear();
  lights.show();
#endif
#if HAS_BRAIN
  pinMode(PIN_PI_EN, OUTPUT);
  digitalWrite(PIN_PI_EN, HIGH);  // power up the Pi (it takes ~30 s to boot)
  Serial1.begin(115200, SERIAL_8N1, D7 /* RX */, D6 /* TX */);
#endif
  setupRadio();
  Serial.printf("Car %d ready\n", CAR_ID);
}

void loop() {
  static uint32_t lastSensor = 0, lastPower = 0, lastTelemetry = 0, lastBrainTelemetry = 0;
  static int prevThrottle = 0;
  uint32_t now = millis();

  if (now - lastSensor >= 40) { lastSensor = now; readDistance(); }
  if (now - lastPower >= 250) { lastPower = now; readPower(); managePiPower(); }
  pollBrain();

  ControlPacket cmd;
  uint32_t cmdMs;
  portENTER_CRITICAL(&rxLock);
  cmd = lastCmd;
  cmdMs = lastCmdMs;
  portEXIT_CRITICAL(&rxLock);
  bool linkOk = cmdMs != 0 && now - cmdMs < LINK_TIMEOUT_MS;

  if (now - lastTelemetry >= 200) { lastTelemetry = now; sendTelemetry(cmd.mode); }
  if (now - lastBrainTelemetry >= 100) { lastBrainTelemetry = now; sendBrainTelemetry(cmd.mode); }

  // ---- parked on the charging pad: no driving, show the charge level ----
  if (charging) {
    setMotor(0);
    currentThrottle = 0;
    setSteer(0);
    showChargeLevel();
    delay(20);
    return;
  }

  int throttle = 0, steer = 0;
  bool warn = false;

  if (!linkOk) {
    warn = true;  // failsafe: lost the controller, so stop and flash hazards
  } else if (cmd.mode == MODE_BRAIN) {
    // The Pi drives, but the controller must stay on (it's the dead-man switch),
    // and any real stick movement takes over instantly.
    bool brainOk = HAS_BRAIN && brainCmd.ms != 0 && now - brainCmd.ms < BRAIN_TIMEOUT_MS;
    bool humanOverride = abs(cmd.throttle) > 30 || abs(cmd.steer) > 30;
    if (humanOverride) {
      throttle = cmd.throttle * MAX_THROTTLE / 100;
      steer = cmd.steer;
    } else if (brainOk) {
      throttle = brainCmd.throttle * MAX_THROTTLE / 100;
      steer = brainCmd.steer;
      bool closeOk = (brainCmd.flags & BRAIN_FLAG_CLOSE_OK) && throttle <= BRAIN_CLOSE_MAX;
      if (!closeOk && throttle > 0 && distanceMm != DISTANCE_NONE && distanceMm < AVOID_STOP_MM) {
        throttle = 0;
        warn = true;
      }
    } else {
      warn = true;  // brain silent (booting, crashed, or not fitted): stop
    }
  } else if (cmd.mode == MODE_AUTO) {
    runAuto(throttle, steer);
    if (cmd.throttle < -50) throttle = 0;  // pull back on the stick = stop the robot
  } else {
    throttle = cmd.throttle * MAX_THROTTLE / 100;
    steer = cmd.steer;
    if (cmd.mode == MODE_AVOID && throttle > 0 && distanceMm != DISTANCE_NONE && distanceMm < AVOID_STOP_MM) {
      throttle = 0;  // refuse to drive into the wall; reverse still works
      warn = true;
    }
  }

  if (batteryMv < LOW_BATTERY_MV) {
    throttle = throttle / 2;  // limp home to the pad
    warn = true;
  }

  driveToward(throttle);
  setSteer(steer);
  showLights(cmd.flags & FLAG_LIGHTS, currentThrottle, prevThrottle, steer, warn);
  prevThrottle = currentThrottle;
  delay(20);
}
