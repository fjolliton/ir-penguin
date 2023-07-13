Delonghi Pinguino IR Controller
===============================

This program emulates the remote control of a Delonghi Pinguino Air
Conditioner.

Usage
-----

You need Python 3 and a compatible IR module (I'm using an IR Toy USB
dongle).

```
$ ./ir-penguin -h
usage: ir-penguin [-h] [-d DEVICE] [--off] [-m MODE] [-s SPEED] [-t TEMP]

options:
  -h, --help            show this help message and exit
  -d DEVICE, --device DEVICE
                        Path to the IR module (default: /dev/lirc0)
  --off                 Turn the device off (default: False)
  -m MODE, --mode MODE  1 for Fan Mode, 2 for Dehumidifier Mode, 3 for Air Conditioner Mode (default: 1)
  -s SPEED, --speed SPEED
                        Fan speed between 1 (slowest) and 3 (fastest) (default: 1)
  -t TEMP, --temp TEMP  Temperature in Celsius (16C to 32C) (default: 20)
```

Missing features
----------------

 - [ ] Setting the temperature in Fahrenheit
 - [ ] Setting the timer

Message format
--------------

Reverse engineered from the remote control.

First byte (Address):

      7   6   5   4   3   2   1   0
    +---+---+---+---+---+---+---+---+
    | 0 | 1 | 0 | 0 | 1 | 0 | 0 | 0 |
    +---+---+---+---+---+---+---+---+

Second byte:

      7   6   5   4   3   2   1   0
    +---+---+---+---+---+---+---+---+
    |      Mode     |   Speed   | 0 |
    +---+---+---+---+---+---+---+---+

 - Mode: either Fan (`1000`), Dehumidifier (`0100`)
   or Air Conditioner (`0001`)
 - Fan speed: either 1 (`001`), 2 (`010`) or 3 (`100`)

Third byte:

      7   6   5   4   3   2   1   0
    +---+---+---+---+---+---+---+---+
    | O | T | F |     Duration      |
    +---+---+---+---+---+---+---+---+

 - O: 0 = Off, 1 = On
 - T: 0 = unset timer, 1 = set timer
 - F: 0 = Celsius, 1 = Fahrenheit
 - Duration: 0x01...0x18 = timer hours (1hr to 24hr).

Fourth byte:

      7   6   5   4   3   2   1   0
    +---+---+---+---+---+---+---+---+
    | 0 |           Temp.           |
    +---+---+---+---+---+---+---+---+

 - Celsius: 0x00...0x10 (T°C - 16, with T in [16...32]).
 - Fahrenheit: 0x3d...0x59 (T°F in [61...89]).
