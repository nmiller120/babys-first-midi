# Baby's First MIDI — Rev A Electrical Specification

This file is the source-of-truth for the first ERC-checkable KiCad schematic.

## Architecture

External project box. The Pimoroni Tiny 2350 is powered through its onboard USB-C connector.

Signal flow:

Fisher-Price toy -> RJ45 -> 5x MOSFET input buffers -> Tiny 2350 -> TRS MIDI OUT

Two 10k potentiometers connect directly to Tiny 2350 analog inputs.

## RJ45 pin assignment

| RJ45 pin | Signal |
| --- | --- |
| 1 | FPT_C |
| 2 | FPT_D |
| 3 | FPT_E |
| 4 | FPT_F |
| 5 | FPT_G |
| 6 | FPT_COMMON |
| 7 | Spare |
| 8 | Spare |

## Digital input buffers

Five identical IRLZ44N channels are used.

For each channel:

- Fisher-Price sense line -> 100k ohm -> IRLZ44N gate
- IRLZ44N source -> GND
- IRLZ44N drain -> Tiny 2350 GPIO
- 3V3 -> 10k ohm pull-up -> drain/GPIO node

This is an inverting open-drain-style buffer stage.

| Key | Tiny 2350 GPIO |
| --- | --- |
| C | GP1 |
| D | GP2 |
| E | GP3 |
| F | GP4 |
| G | GP5 |

## Potentiometers

Both potentiometers are 10k.

| Function | Tiny 2350 pin |
| --- | --- |
| Octave | GP26 / ADC0 / A0 |
| Scale | GP27 / ADC1 / A1 |

Each pot is wired as a 3.3V-to-GND divider with the wiper going to the ADC input.

## MIDI OUT

UART0 TX is GP0 at 31,250 baud.

TRS Type A output:

- 3V3 -> 33 ohm -> Ring
- GP0 -> 33 ohm -> Tip
- Sleeve -> NC

## Power

The Tiny 2350 is powered only through its onboard USB-C connector for Rev A.

No Fisher-Price power is brought into the project box.

## Schematic intent

The KiCad schematic should contain:

- J1: 8-pin RJ45 female connector
- Q1-Q5: IRLZ44N
- R1-R5: 100k gate resistors
- R6-R10: 10k GPIO pull-ups
- U1: Pimoroni Tiny 2350 module/header representation
- RV1: 10k octave potentiometer
- RV2: 10k scale potentiometer
- R11-R12: 33 ohm MIDI series resistors
- J2: 3.5mm TRS jack
- Explicit 3V3 and GND nets
- No-connect markers on unused RJ45 pins and TRS sleeve where appropriate

Before Gerber generation, the schematic must pass ERC with no unexplained errors and the PCB must pass DRC with no unexplained errors.
