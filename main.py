from machine import UART, Pin
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

# Tiny 2350 onboard RGB LED is on GP18-GP20 and is active-low.
led_r = Pin(18, Pin.OUT, value=1)
led_g = Pin(19, Pin.OUT, value=1)
led_b = Pin(20, Pin.OUT, value=1)

# Fisher-Price keys are expected to be active-high.
# For bench testing with jumpers, enable the RP2350's internal pull-downs
# so each input has a defined LOW state when nothing is connected.
#
# Standard MIDI note numbers:
# C3=48, D3=50, E3=52, F3=53, G3=55
BUTTON_CONFIG = (
    (1, 48),  # GP1 -> C3
    (2, 50),  # GP2 -> D3
    (3, 52),  # GP3 -> E3
    (4, 53),  # GP4 -> F3
    (5, 55),  # GP5 -> G3
)


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


buttons = []
active_notes = set()

for gpio, note in BUTTON_CONFIG:
    pin = Pin(gpio, Pin.IN, Pin.PULL_DOWN)
    initial_state = pin.value()

    buttons.append({
        "pin": pin,
        "note": note,
        "raw_state": initial_state,
        "stable_state": initial_state,
        "changed_at": ticks_ms(),
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
            note = button["note"]

            if raw_state:
                # Note stays on for as long as the input remains HIGH.
                note_on(note)
                active_notes.add(note)
            else:
                note_off(note)
                active_notes.discard(note)

            # Keep the LED lit while one or more notes are being sustained.
            set_led(bool(active_notes))

    # Each key is debounced independently, so multiple held keys remain
    # active at once and the controller stays polyphonic.
    sleep_ms(1)
