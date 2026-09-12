from machine import UART, Pin, ADC, SoftI2C
from time import sleep_ms, ticks_ms, ticks_diff


# USB console logging. MIDI UART output is independent of this flag.
DEBUG = False


def debug_print(*args):
    if DEBUG:
        print(*args)


# Same OLED wiring and software I2C as the successful Test003.
# Send 32 display bytes per main-loop pass, rather than blocking key scanning
# for an entire 1024-byte frame (about 100 ms at 100 kHz).
OLED_WIDTH = 128
OLED_HEIGHT = 64
OLED_CHUNK_SIZE = 32
display = None
display_selection = None
display_offset = OLED_WIDTH * OLED_HEIGHT // 8


def init_display():
    global display
    try:
        from ssd1306 import SSD1306_I2C
        i2c = SoftI2C(sda=Pin(6), scl=Pin(7), freq=100_000)
        sleep_ms(100)
        devices = i2c.scan()
        address = next((a for a in (0x3C, 0x3D) if a in devices), None)
        if address is None:
            debug_print("OLED | No screen found at 0x3C or 0x3D")
            return
        display = SSD1306_I2C(OLED_WIDTH, OLED_HEIGHT, i2c, addr=address)
        display.contrast(128)
    except (ImportError, OSError) as error:
        display = None
        debug_print("OLED | Disabled:", error)


def update_display():
    global display, display_selection, display_offset
    if display is None:
        return
    try:
        # Finish the current snapshot before drawing a newer selection.
        if display_offset >= len(display.buffer):
            selection = (last_octave_index, last_scale_index)
            if selection == display_selection:
                return
            octave_name, ko2_group, _ = OCTAVE_ROOTS[selection[0]]
            scale_name, _ = SCALES[selection[1]]
            display.fill(0)
            display.text("OCTAVE: " + octave_name, 0, 0)
            display.text("KO II GROUP: " + ko2_group, 0, 16)
            display.text("SCALE:", 0, 36)
            display.text(scale_name, 0, 48)
            # Horizontal addressing: start a fresh full-screen transfer.
            for command in (0x21, 0, OLED_WIDTH - 1, 0x22, 0, OLED_HEIGHT // 8 - 1):
                display.write_cmd(command)
            display_selection = selection
            display_offset = 0
        end = min(display_offset + OLED_CHUNK_SIZE, len(display.buffer))
        display.write_data(memoryview(display.buffer)[display_offset:end])
        display_offset = end
    except OSError as error:
        # A disconnected screen must not stop Note Off processing.
        display = None
        debug_print("OLED | Disabled after transfer error:", error)


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
POT_HYSTERESIS = 2000
POT_DEBOUNCE_MS = 150

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
    Return the raw selector region with no hysteresis.
    Used only to establish the initial selector state at startup.
    """
    raw = adc.read_u16()
    raw = max(POT_ADC_MIN, min(raw, POT_ADC_MAX))

    span = POT_ADC_MAX - POT_ADC_MIN
    normalized = raw - POT_ADC_MIN

    index = (normalized * option_count) // (span + 1)
    return min(index, option_count - 1)


def hysteresis_index(adc, option_count, current_index):
    """
    Update a discrete pot selector using hysteresis around each boundary.

    The knob must move POT_HYSTERESIS counts past a boundary before the
    state changes. Once changed, it must move back past the opposite side
    of that deadband before changing back.
    """
    raw = adc.read_u16()
    raw = max(POT_ADC_MIN, min(raw, POT_ADC_MAX))

    span = POT_ADC_MAX - POT_ADC_MIN
    region_width = span / option_count

    # Allow large knob movements to cross more than one state in one pass.
    while current_index < option_count - 1:
        upper_boundary = POT_ADC_MIN + ((current_index + 1) * region_width)
        if raw >= upper_boundary + POT_HYSTERESIS:
            current_index += 1
        else:
            break

    while current_index > 0:
        lower_boundary = POT_ADC_MIN + (current_index * region_width)
        if raw <= lower_boundary - POT_HYSTERESIS:
            current_index -= 1
        else:
            break

    return current_index


def note_for_key(key_index):
    octave_name, ko2_group, root_note = OCTAVE_ROOTS[last_octave_index]
    scale_name, intervals = SCALES[last_scale_index]
    note = root_note + intervals[key_index]

    return note, octave_name, ko2_group, scale_name


buttons = []
active_notes = set()

# Stable selector states drive MIDI notes, the OLED, and optional debug output.
last_octave_index = pot_index(octave_pot, len(OCTAVE_ROOTS))
last_scale_index = pot_index(scale_pot, len(SCALES))

octave_candidate_index = last_octave_index
scale_candidate_index = last_scale_index
octave_candidate_since = ticks_ms()
scale_candidate_since = ticks_ms()

octave_name, ko2_group, _ = OCTAVE_ROOTS[last_octave_index]
scale_name, _ = SCALES[last_scale_index]

debug_print(
    "OCTAVE | Octave: {} | KO II Group: {}".format(
        octave_name, ko2_group
    )
)
debug_print("SCALE  | Scale: {}".format(scale_name))

for key_index, gpio in enumerate(BUTTON_GPIOS):
    pin = Pin(gpio, Pin.IN)
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


init_display()

while True:
    now = ticks_ms()

    octave_index = hysteresis_index(
        octave_pot, len(OCTAVE_ROOTS), last_octave_index
    )

    if octave_index != octave_candidate_index:
        octave_candidate_index = octave_index
        octave_candidate_since = now

    if (
        octave_candidate_index != last_octave_index
        and ticks_diff(now, octave_candidate_since) >= POT_DEBOUNCE_MS
    ):
        last_octave_index = octave_candidate_index
        octave_name, ko2_group, root_note = OCTAVE_ROOTS[last_octave_index]
        debug_print(
            "OCTAVE | Octave: {} | KO II Group: {} | Root MIDI Note: {}".format(
                octave_name, ko2_group, root_note
            )
        )

    scale_index = hysteresis_index(
        scale_pot, len(SCALES), last_scale_index
    )

    if scale_index != scale_candidate_index:
        scale_candidate_index = scale_index
        scale_candidate_since = now

    if (
        scale_candidate_index != last_scale_index
        and ticks_diff(now, scale_candidate_since) >= POT_DEBOUNCE_MS
    ):
        last_scale_index = scale_candidate_index
        scale_name, _ = SCALES[last_scale_index]
        debug_print("SCALE  | Scale: {}".format(scale_name))

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

                debug_print(
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

    update_display()

    # Independent debounce keeps simultaneous key presses polyphonic.
    sleep_ms(1)
