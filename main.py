from machine import UART, Pin, ADC
from time import sleep_ms, ticks_ms, ticks_diff

# MIDI 1.0 serial: 31,250 baud, 8-N-1.
# Tiny 2350: UART0 TX on GP0.
midi = UART(
    0,
    baudrate=31250,
    tx=Pin(0)
)

MIDI_CHANNEL = 1
MIDI_VELOCITY = 100
DEBOUNCE_MS = 30

# Calibrated usable range of both 10k potentiometers.
# Clamp the physical end regions so every selector position is easy to reach.
POT_ADC_MIN = 1000
POT_ADC_MAX = 56000

# Tiny 2350 onboard RGB LED is on GP18-GP20 and is active-low.
led_r = Pin(18, Pin.OUT, value=1)
led_g = Pin(19, Pin.OUT, value=1)
led_b = Pin(20, Pin.OUT, value=1)

# Tiny 2350 analog inputs.
# A0 = GP26 / ADC0
# A1 = GP27 / ADC1
octave_pot = ADC(26)
scale_pot = ADC(27)

# A0 selects the C-root octave. These line up with the KO II's
# four fixed MIDI note groups:
# C2=36 -> Group A
# C3=48 -> Group B
# C4=60 -> Group C
# C5=72 -> Group D
OCTAVE_ROOTS = (
    ("C2", "A", 36),
    ("C3", "B", 48),
    ("C4", "C", 60),
    ("C5", "D", 72),
)

# A1 selects the interval pattern used by the five keys.
# Intervals are semitones above the selected C root.
SCALES = (
    ("Chromatic",       (0, 1, 2, 3, 4)),
    ("Major",           (0, 2, 4, 5, 7)),
    ("Minor",           (0, 2, 3, 5, 7)),
    ("Minor Pentatonic",(0, 3, 5, 7, 10)),
    ("Major Pentatonic",(0, 2, 4, 7, 9)),
)

# Fisher-Price keys are expected to be active-high.
# Internal pull-downs keep the inputs defined during jumper testing.
BUTTON_GPIOS = (1, 2, 3, 4, 5)


def set_led(on):
    # White when any note is active. Active-low outputs.
    value = 0 if on else 1
    led_r.value(value)
    led_g.value(value)
    led_b.value(value)


def note_on(note, velocity=MIDI_VELOCITY, channel=MIDI_CHANNEL):
    status = 0x90 | ((channel - 1) & 0x0F)
    midi.write(bytes((status, note, velocity)))


def note_off(note, velocity=0, channel=MIDI_CHANNEL):
    status = 0x80 | ((channel - 1) & 0x0F)
    midi.write(bytes((status, note, velocity)))


def pot_index(adc, option_count):
    """
    Divide the calibrated potentiometer range into equal-width settings.

    Values at or below POT_ADC_MIN select the first setting.
    Values at or above POT_ADC_MAX select the last setting.
    """
    raw = adc.read_u16()
    raw = max(POT_ADC_MIN, min(raw, POT_ADC_MAX))

    span = POT_ADC_MAX - POT_ADC_MIN
    normalized = raw - POT_ADC_MIN

    # Map the full calibrated range across all available settings.
    index = (normalized * option_count) // (span + 1)
    return min(index, option_count - 1)


def selected_root():
    return OCTAVE_ROOTS[pot_index(octave_pot, len(OCTAVE_ROOTS))]


def selected_scale():
    return SCALES[pot_index(scale_pot, len(SCALES))]


def note_for_key(key_index):
    octave_name, ko2_group, root_note = selected_root()
    scale_name, intervals = selected_scale()
    note = root_note + intervals[key_index]

    return note, octave_name, ko2_group, scale_name


buttons = []
active_notes = set()

for key_index, gpio in enumerate(BUTTON_GPIOS):
    pin = Pin(gpio, Pin.IN, Pin.PULL_DOWN)
    initial_state = pin.value()

    buttons.append({
        "pin": pin,
        "key_index": key_index,
        "raw_state": initial_state,
        "stable_state": initial_state,
        "changed_at": ticks_ms(),
        # Remember the exact note started by this key so Note Off still
        # targets the correct note if either pot moves while it is held.
        "active_note": None,
    })


while True:
    now = ticks_ms()

    for button in buttons:
        raw_state = button["pin"].value()

        # A raw transition starts/restarts this button's debounce timer.
        if raw_state != button["raw_state"]:
            button["raw_state"] = raw_state
            button["changed_at"] = now

        # Accept a new state only after it remains unchanged for DEBOUNCE_MS.
        if (
            raw_state != button["stable_state"]
            and ticks_diff(now, button["changed_at"]) >= DEBOUNCE_MS
        ):
            button["stable_state"] = raw_state

            if raw_state:
                # Read both pots at the instant the key is pressed.
                note, octave_name, ko2_group, scale_name = note_for_key(
                    button["key_index"]
                )
                button["active_note"] = note

                print(
                    "PRESS | Octave: {} | KO II Group: {} | Scale: {} | MIDI Note: {}".format(
                        octave_name,
                        ko2_group,
                        scale_name,
                        note,
                    )
                )

                note_on(note)
                active_notes.add(note)
            else:
                note = button["active_note"]

                if note is not None:
                    note_off(note)
                    active_notes.discard(note)
                    button["active_note"] = None

            # Keep the LED lit while one or more notes are sustained.
            set_led(bool(active_notes))

    # Independent debounce keeps simultaneous key presses polyphonic.
    sleep_ms(1)
