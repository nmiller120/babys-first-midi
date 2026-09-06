# Baby's First MIDI

A Fisher-Price piano hacked into a MIDI controller while preserving the toy's original functionality.

## Hardware

- Pimoroni Tiny 2350 (RP2350, 3.3 V logic)
- Fisher-Price Kick & Play-style piano
- 3.5 mm TRS Type A MIDI output
- Teenage Engineering EP-133 K.O. II as the first MIDI target

## Project plan

1. Prove Tiny 2350 -> MIDI OUT -> KO II communication.
2. Characterize the five Fisher-Price key signals.
3. Read the keys without disrupting the stock toy electronics.
4. Send independent MIDI Note On / Note Off messages for polyphonic play.
5. Power the Tiny 2350 from the toy's existing 3xAA battery pack if practical.

## MIDI bench test

Tiny 2350 UART0 TX is on GP0 for the initial test. MIDI serial is 31,250 baud.

The 3.3 V MIDI transmitter target values are 33 ohm and 10 ohm. The current breadboard uses 20 ohm + 10 ohm in series (30 ohm) as a temporary approximation to 33 ohm:

    Tiny 2350                     TRS Type A MIDI
    ---------                     ---------------
    3V3 --- 20R --- 10R -------- Ring
    GP0 ----------- 10R -------- Tip
    GND                         (not connected)
                                Sleeve: NC

IMPORTANT: Verify wiring and polarity before connecting an instrument. The KO II uses TRS MIDI Type A.

## Software

The first firmware target is MicroPython.

`main.py` sends a repeating middle-C MIDI Note On / Note Off over UART0 TX / GP0.

Once the bench test works, the timer-based test will be replaced with five GPIO inputs from the Fisher-Price keys.

## Status

Early hardware prototype.
