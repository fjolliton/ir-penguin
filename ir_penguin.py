#!/usr/bin/env python3

import struct
import argparse


def int_interval(name, a, b):
    def parse(val):
        val = int(val)
        if not (a <= val <= b):
            raise argparse.ArgumentTypeError(f"{name} should be between {a} and {b}")
        return val

    return parse


parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument(
    "-d", "--device", help="Path to the IR module", default="/dev/lirc0"
)
parser.add_argument("--off", action="store_true", help="Turn the device off")
parser.add_argument(
    "-m",
    "--mode",
    type=int_interval("mode", 1, 3),
    default=1,
    help="1 for Fan Mode, 2 for Dehumidifier Mode, 3 for Air Conditioner Mode",
)
parser.add_argument(
    "-s",
    "--speed",
    type=int_interval("speed", 1, 3),
    default=1,
    help="Fan speed between 1 (slowest) and 3 (fastest)",
)
parser.add_argument(
    "-t",
    "--temp",
    type=int_interval("temp", 16, 32),
    default=21,
    help="Temperature in Celsius (16C to 32C)",
)


def encode(value):
    """
    Encode a byte with the NEC protocol

    Timings are given in µs.
    """
    assert 0 <= value <= 255
    for i in range(8):
        b = value & (1 << i)
        yield 560
        yield 1690 if b else 565


def encode_full(msg):
    """
    Encode a whole message with NEC protocol

    Timings are given in µs.
    """
    assert len(msg) == 4 and all(0 <= b <= 255 for b in msg)
    yield 9000
    yield 4500
    for value in msg:
        yield from encode(value)
    yield 560


def make_pinguino_command(*, on=True, mode=1, speed=1, temp=20):
    yield from encode_full(
        [
            # Byte 1
            0x48,
            # Byte 2
            (0x80 if mode == 1 else 0x40 if mode == 2 else 0x10)
            | (0x02 if speed == 1 else 0x04 if speed == 2 else 0x08),
            # Byte 3
            (0x80 if on else 0x00) | 0x01,
            # Byte 4
            max(16, min(temp, 32)) - 16,
        ]
    )


def main():
    ns = parser.parse_args()

    # Summary
    mode_name = (
        "Fan only"
        if ns.mode == 1
        else "Dehumidifier"
        if ns.mode == 2
        else "Air Conditioner"
    )
    fan_speed_name = "low" if ns.speed == 1 else "medium" if ns.speed == 2 else "high"
    print(f"Operating Mode: {mode_name}")
    print(f"Fan Speed:      {ns.speed} ({fan_speed_name})")
    print(f"Target Temp:    {ns.temp}°C")

    cmd = make_pinguino_command(
        on=not ns.off, mode=ns.mode, speed=ns.speed, temp=ns.temp
    )
    data = b"".join(struct.pack("<I", timing) for timing in cmd)
    with open(ns.device, "wb") as f:
        f.write(data)


if __name__ == "__main__":
    main()
