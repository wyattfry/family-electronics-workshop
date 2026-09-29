#!/usr/bin/env bash
# Unit 16's three sketches each carry a copy of protocol.h; make sure they match.
set -euo pipefail
dir="$(cd "$(dirname "$0")/.." && pwd)/units/16-micro-rc-cars/firmware"
ref="$dir/car/protocol.h"
for f in "$dir"/controller/protocol.h "$dir"/pad/protocol.h; do
  cmp -s "$ref" "$f" || { echo "MISMATCH: $f differs from car/protocol.h"; exit 1; }
done
echo "protocol.h copies match"
