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

# Fisher-Price keys are expected to be active-high.
# Use plain inputs (no internal pull-ups) so the Tiny 2350 does not
# bias the toy's existing 3.3 V key signals.
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


def note_on(note, velocity=MIDI_VELOCITY, channel=MIDI_CHANNEL):
    status = 0x90 | ((channel - 1) & 0x0F)
    midi.write(bytes((status, note, velocity)))


def note_off(note, velocity=0, channel=MIDI_CHANNEL):
    status = 0x80 | ((channel - 1) & 0x0F)
    midi.write(bytes((status, note, velocity)))


buttons = []

for gpio, note in BUTTON_CONFIG:
    pin = Pin(gpio, Pin.IN)
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

        # Only accept the new state after it has remained unchanged
        # for the full debounce interval.
        if (
            raw_state != button["stable_state"]
            and ticks_diff(now, button["changed_at"]) >= DEBOUNCE_MS
        ):
            button["stable_state"] = raw_state

            if raw_state:
                note_on(button["note"])
            else:
                note_off(button["note"])

    # A short polling delay keeps the loop responsive while avoiding
    # unnecessary CPU churn. Each button is debounced independently,
    # so simultaneous key presses remain polyphonic.
    sleep_ms(1)
