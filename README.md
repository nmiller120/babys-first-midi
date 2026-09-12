# Baby's First MIDI

A Fisher-Price piano hacked into a MIDI controller while preserving the toy's original functionality.

## Hardware

- Pimoroni Tiny 2350 (RP2350, 3.3 V logic)
- Fisher-Price Kick & Play-style piano
- Teenage Engineering EP-133 K.O. II as the initial MIDI target
- 3.5 mm TRS Type A MIDI output
- Two 10k potentiometers for octave/group and scale selection

## Current controller layout

### Piano keys

Five active-high digital inputs are mapped to the Fisher-Price piano keys:

| Tiny 2350 GPIO | Key |
| --- | --- |
| GP1 | Key 1 |
| GP2 | Key 2 |
| GP3 | Key 3 |
| GP4 | Key 4 |
| GP5 | Key 5 |

The GPIOs are configured as plain digital inputs with no internal pull-up or pull-down. A press sends MIDI Note On and releasing the key sends MIDI Note Off. Notes sustain for as long as a key is held, and multiple keys can be held simultaneously for polyphonic MIDI.

The key inputs use a 30 ms software debounce.

### A0 - octave / KO II group selector

A 10k potentiometer connected to A0 (GP26 / ADC0) selects the C-root octave:

| Setting | Root MIDI note | KO II group |
| --- | ---: | --- |
| C2 | 36 | A |
| C3 | 48 | B |
| C4 | 60 | C |
| C5 | 72 | D |

This uses the KO II's fixed MIDI note ranges to make the pot function as a physical A/B/C/D group selector.

### A1 - scale selector

A second 10k potentiometer connected to A1 (GP27 / ADC1) selects the interval mapping for the five keys:

| Setting | Five-key mapping |
| --- | --- |
| Chromatic | C, C#, D, D#, E |
| Major | C, D, E, F, G |
| Minor | C, D, Eb, F, G |
| Minor Pentatonic | C, Eb, F, G, Bb |
| Major Pentatonic | C, D, E, G, A |

The root is always C. The A0 octave selection is added to the interval pattern selected by A1 to produce the final MIDI note.

## Potentiometer calibration and filtering

Bench testing showed that both pots reach approximately 56,000 at the top of their useful ADC range rather than the full 65,535 returned by MicroPython's `read_u16()`.

The selector logic therefore uses a calibrated range:

    POT_ADC_MIN = 1000
    POT_ADC_MAX = 56000

Readings outside that range are clamped to the nearest endpoint. This provides usable dead zones at both physical ends of the pots and ensures the first and last selector positions are easy to reach.

To prevent ADC noise from causing selector chatter near a boundary, two filters are applied:

    POT_HYSTERESIS = 2000
    POT_DEBOUNCE_MS = 150

A pot must first move beyond the hysteresis boundary and then remain in the new discrete state for at least 150 ms before the selection is accepted.

The stable filtered selector state is also used when calculating MIDI notes, so debug output and actual MIDI behavior remain synchronized.

## MIDI output

Tiny 2350 UART0 TX is on GP0. MIDI serial runs at 31,250 baud.

The current 3.3 V MIDI transmitter breadboard is:

    Tiny 2350                     TRS Type A MIDI
    ---------                     ---------------
    3V3 --- 20R --- 10R -------- Ring
    GP0 ----------- 10R -------- Tip
    GND                         (not connected)
                                Sleeve: NC

The 20 ohm + 10 ohm series pair is a temporary 30 ohm approximation to the nominal 33 ohm transmitter resistor used in the 3.3 V MIDI circuit.

IMPORTANT: Verify wiring and polarity before connecting an instrument. The KO II uses TRS MIDI Type A.

## LED behavior

The Tiny 2350 onboard RGB LED is used as a MIDI activity indicator. It lights white while one or more notes are being held and turns off when the final active note is released.

## Debug output

During development, `main.py` prints state changes to the MicroPython console.

Changing the octave/group pot produces output similar to:

    OCTAVE | Octave: C4 | KO II Group: C | Root MIDI Note: 60

Changing the scale pot produces:

    SCALE  | Scale: Minor Pentatonic

Pressing a key reports the complete transformation:

    PRESS | Octave: C4 | KO II Group: C | Scale: Minor Pentatonic | MIDI Note: 67

This makes it possible to verify the pot selection, scale mapping, and resulting MIDI note from Thonny without relying solely on the KO II.

## Tests

The `Tests` directory contains development/bench scripts.

- `Test001.py` - initial UART MIDI and onboard LED test.
- `Test002.py` - periodically prints raw A0/A1 ADC readings and approximate voltages for potentiometer testing and calibration.

## Development status

Current development branch: `feature/pot-scale-selection`.

Completed so far:

- Tiny 2350 MicroPython environment
- 31,250 baud MIDI UART output
- TRS Type A KO II MIDI communication
- Five debounced digital key inputs
- Sustained Note On / Note Off behavior
- Polyphonic key handling
- Onboard MIDI activity LED
- Four-position octave / KO II group selection
- Five-position scale selection
- Potentiometer ADC calibration
- Potentiometer hysteresis and time debounce
- Thonny debug logging

Next major hardware step is integrating the Tiny 2350 inputs with the Fisher-Price key signals while preserving the toy's original functionality.
