// Shared ESP-NOW message formats for the car, controller, and charging pad.
// KEEP THIS FILE IDENTICAL in car/, controller/, and pad/ (Arduino can't share
// headers between sketch folders). tools/check_protocol.sh verifies it.
#pragma once
#include <stdint.h>

constexpr uint8_t PROTO_MAGIC = 0xC7;
constexpr uint8_t WIFI_CHANNEL = 1;  // everyone must be on the same channel

enum MsgType : uint8_t { MSG_CONTROL = 1, MSG_TELEMETRY = 2 };

enum Mode : uint8_t {
  MODE_MANUAL = 0,  // you drive
  MODE_AVOID = 1,   // you drive, the car refuses to hit things
  MODE_AUTO = 2,    // the car drives itself and steers around obstacles
  MODE_BRAIN = 3,   // the Pi "brain" module drives; your sticks override it
  MODE_COUNT = 4,
};

enum ControlFlags : uint8_t { FLAG_LIGHTS = 1 << 0 };

// Controller -> car, ~50 times a second. Broadcast; the car ignores other car IDs.
struct __attribute__((packed)) ControlPacket {
  uint8_t magic;     // PROTO_MAGIC
  uint8_t type;      // MSG_CONTROL
  uint8_t carId;     // 1..9
  int8_t throttle;   // -100 (full reverse) .. +100 (full forward)
  int8_t steer;      // -100 (full left) .. +100 (full right)
  uint8_t mode;      // Mode
  uint8_t flags;     // ControlFlags
  uint8_t seq;       // increments every packet (lets you count dropped packets)
};

// Car -> controller and pad, ~5 times a second.
constexpr uint16_t DISTANCE_NONE = 0xFFFF;
struct __attribute__((packed)) TelemetryPacket {
  uint8_t magic;        // PROTO_MAGIC
  uint8_t type;         // MSG_TELEMETRY
  uint8_t carId;
  uint8_t batteryPct;   // 0..100
  uint16_t batteryMv;
  uint16_t distanceMm;  // DISTANCE_NONE if nothing seen
  uint8_t charging;     // 1 while sitting on the pad
  uint8_t mode;
};
