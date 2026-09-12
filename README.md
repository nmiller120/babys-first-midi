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

## OLED readout

`main.py` shows the stable octave (C2-C5), KO II group (A-D), and full scale
name on the 128x64 SSD1306 OLED. It uses the same working SoftI2C setup as
Test003: SDA=GP6, SCL=GP7, VCC=3V3, GND=GND at 100 kHz. Keep the bundled
`Tests/ssd1306.py` installed as `/lib/ssd1306.py` on the Tiny.

The readout follows the filtered selections used for MIDI notes. Screen
updates occur on startup and selection changes, with 32-byte transfers
between key scans. A missing driver/display or I2C error disables the
readout for that run while the MIDI controller continues. Restart after
fixing the connection to enable the display again.

To deploy, open the updated `main.py` in Thonny and save it to the Tiny as
`/main.py`. Run it with F5; it will also run on subsequent board resets.

## Debug output

`main.py` has a hardcoded `DEBUG = False` flag near the top. Set it to `True`
to print startup selections, pot changes, key presses, and display diagnostics
to the USB MicroPython console. With `False`, application logging is silent;
MIDI UART messages and OLED updates still operate. MicroPython's own boot
banner and unhandled tracebacks are not controlled by this flag.

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
- `Test003.py` - SSD1306 128x64 I2C OLED hello-world test with a changing counter.

### Running Test003: OLED hello world

For the Hosyond 0.96-inch 128x64 SSD1306 I2C module (Amazon B09T6SJBV5):

| Display label | Tiny 2350 connection |
| --- | --- |
| GND | GND |
| VCC | 3V3 |
| SDA | GP6 |
| SCL | GP7 |

Wire with power disconnected and follow the printed labels, not the physical
header order. Power this module from 3V3 so its I2C pull-ups use 3.3 V logic.
These are the Tiny's numbered GPIO pins, not its separate Qw/ST connector.

1. Connect the Tiny in Thonny using its MicroPython interpreter. Stop the
   running controller with Stop/Restart or Ctrl+C.
2. Save the bundled `Tests/ssd1306.py` onto the Tiny as
   `/lib/ssd1306.py` (create the `lib` folder if needed).
3. Open `Tests/Test003.py` in Thonny and click Run. It can run from the
   computer; there is no need to replace the Tiny's `main.py`.
4. The console prints discovered I2C addresses. The screen should show
   **Hello world!**, **Baby's First MIDI - Test003** across two lines, the
   selected address, and a count updated approximately once per second.
5. Press Ctrl+C to stop; the script blanks the screen.

The test uses software I2C (SoftI2C) at 100 kHz and detects 0x3C or 0x3D (preferring 0x3C if
both respond). An address response alone does not identify the controller;
this test expects the SSD1306 module listed above. If nothing is detected,
check power and the SDA/SCL wiring. An import error means the driver has not
been saved to the Tiny's `/lib` folder. This is a standalone display test;
it does not run the piano/MIDI controller at the same time.

The bundled driver is an unmodified copy from
[MicroPython's SSD1306 driver](https://github.com/micropython/micropython-lib/blob/master/micropython/drivers/display/ssd1306/ssd1306.py),
Git blob `37ad682de94a11687c6afdac8cdc4dc88eb2b46c`.
Its license is included in `Tests/LICENSE-ssd1306.txt`.

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
