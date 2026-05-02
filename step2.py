"""
Step 2: Encode the predicted fall-down location as a WSPR message.

Callsign: SI4NAT  (SIddarth 4 NATarajan)

Outputs
-------
1. Callsign hex
2. Location (offset from start point) + 30 dBm power level hex

WSPR encoding rules (simplified, per lab spec)
-----------------------------------------------
Callsign — 6 characters:
  Ch1        : 0-9 → 0-9,  A-Z → 10-35,  space → 36   (37 choices)
  Ch2        : 0-9 → 0-9,  A-Z → 10-35                 (36 choices, no space)
  Ch3        : 0-9 only                                  (10 choices)
  Ch4-Ch6    : A-Z → 0-25, space → 26                   (27 choices, no digits)
  Formula    : (((([c1]*36+[c2])*10+[c3])*27+[c4])*27+[c5])*27+[c6]

Location + power — 22 bits:
  1. offset   = abs(predicted - start_gps)  for lat and lon
  2. 7-bit fp  = Bits(e4m3float=offset).uint & 0x7F  (drop sign bit)
  3. 15-bit   = 0b0 + lat_7bits + lon_7bits
  4. 22-bit   = 15-bit coord + 7-bit power (30 dBm = 0b0011110 = 30)
"""

import csv
import numpy as np
from bitstring import Bits


# ---------------------------------------------------------------------------
# GPS helpers (mirror of step1b.py so this file runs standalone)
# ---------------------------------------------------------------------------

def load_gps(path):
    times, lats, lons = [], [], []
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            times.append(float(row["time_s"]))
            lats.append(float(row["latitude"]))
            lons.append(float(row["longitude"]))
    return np.array(times), np.array(lats), np.array(lons)


def predict_fall_location(gps_path, runout_time_s):
    times, lats, lons = load_gps(gps_path)
    pred_lat = np.polyval(np.polyfit(times, lats, 2), runout_time_s)
    pred_lon = np.polyval(np.polyfit(times, lons, 2), runout_time_s)
    return float(pred_lat), float(pred_lon)


# ---------------------------------------------------------------------------
# WSPR callsign encoding
# ---------------------------------------------------------------------------

def _char_code(ch, position):
    """Map a character to its WSPR integer code at positions 1-6."""
    c = ch.upper()
    if c.isdigit():
        code = int(c)
    elif c.isalpha():
        code = ord(c) - ord('A') + 10
    else:
        code = 36  # space

    # Ch4-Ch6 accept only A-Z / space; subtract 10 to collapse range to 0-26
    if position >= 4:
        code -= 10
    return code


def encode_callsign(callsign):
    """
    Encode a 6-character WSPR callsign and return its uppercase hex string.

    Callsign constraints:
      - Exactly 6 characters
      - Ch3 must be a digit
      - Ch4-Ch6 must be A-Z or space (no digits)
    """
    assert len(callsign) == 6, "Callsign must be exactly 6 characters"
    c = [_char_code(ch, i + 1) for i, ch in enumerate(callsign)]
    n = (((((c[0] * 36 + c[1]) * 10 + c[2]) * 27 + c[3]) * 27 + c[4]) * 27 + c[5])
    return format(n, 'X')


# ---------------------------------------------------------------------------
# WSPR location + power encoding
# ---------------------------------------------------------------------------

def _to_7bit_fp(value):
    """
    Convert a positive float to its e4m3float 8-bit representation,
    then return the lower 7 bits (dropping the sign bit).
    """
    return Bits(e4m3float=float(value)).uint & 0x7F


def encode_location_power(pred_lat, pred_lon, start_lat, start_lon, power_dbm=30):
    """
    Encode predicted location offset and transmit power into a 22-bit WSPR
    value and return its zero-padded 6-character uppercase hex string.
    """
    dlat = abs(pred_lat - start_lat)
    dlon = abs(pred_lon - start_lon)

    lat_7 = _to_7bit_fp(dlat)
    lon_7 = _to_7bit_fp(dlon)

    # 15-bit: leading 0 (sign=positive) | 7-bit lat | 7-bit lon
    coord_15 = (lat_7 << 7) | lon_7

    # 22-bit: 15-bit coord | 7-bit power
    value_22 = (coord_15 << 7) | (power_dbm & 0x7F)

    return format(value_22, '06X')


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    GPS_PATH     = "gps_data.csv"
    CALLSIGN     = "SI4NAT"   # SIddarth 4 NATarajan
    RUNOUT_TIME  = 10800       # 3 hours in seconds
    POWER_DBM    = 30

    # ---- Callsign ----
    callsign_hex = encode_callsign(CALLSIGN)
    print("=== WSPR Callsign ===")
    print(f"  Callsign : {CALLSIGN}")
    print(f"  Hex      : {callsign_hex}")

    # ---- Location ----
    times, lats, lons = load_gps(GPS_PATH)
    start_lat, start_lon = lats[0], lons[0]
    pred_lat, pred_lon   = predict_fall_location(GPS_PATH, RUNOUT_TIME)

    dlat = abs(pred_lat - start_lat)
    dlon = abs(pred_lon - start_lon)

    lat_7 = _to_7bit_fp(dlat)
    lon_7 = _to_7bit_fp(dlon)
    loc_hex = encode_location_power(pred_lat, pred_lon, start_lat, start_lon, POWER_DBM)

    print("\n=== WSPR Location + Power ===")
    print(f"  GPS start      : ({start_lat:.6f}, {start_lon:.6f})")
    print(f"  Predicted fall : ({pred_lat:.6f}, {pred_lon:.6f})")
    print(f"  Offset         : dlat={dlat:.6f}, dlon={dlon:.6f}")
    print(f"  lat 7-bit fp   : {lat_7:07b}  ({lat_7})")
    print(f"  lon 7-bit fp   : {lon_7:07b}  ({lon_7})")
    print(f"  15-bit coord   : {((lat_7 << 7) | lon_7):015b}")
    print(f"  Power ({POWER_DBM} dBm) : {POWER_DBM:07b}")
    print(f"  Hex (22-bit)   : {loc_hex}")

    print("\n=== Report Summary ===")
    print(f"  1. Callsign              : {CALLSIGN}")
    print(f"  2. Callsign hex          : {callsign_hex}")
    print(f"  3. Predicted fall location: ({pred_lat:.6f}, {pred_lon:.6f})")
    print(f"  4. Location + power hex  : {loc_hex}")


if __name__ == "__main__":
    main()
