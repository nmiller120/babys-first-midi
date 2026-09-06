from machine import UART, Pin
from time import sleep

# MIDI 1.0 serial: 31,250 baud, 8-N-1.
# Tiny 2350: UART0 TX on GP0.
midi = UART(
    0,
    baudrate=31250,
    tx=Pin(0)
)

MIDI_CHANNEL = 1
TEST_NOTE = 60       # Middle C
TEST_VELOCITY = 100


def note_on(note, velocity=100, channel=1):
    status = 0x90 | ((channel - 1) & 0x0F)
    midi.write(bytes((status, note, velocity)))


def note_off(note, velocity=0, channel=1):
    status = 0x80 | ((channel - 1) & 0x0F)
    midi.write(bytes((status, note, velocity)))


while True:
    note_on(TEST_NOTE, TEST_VELOCITY, MIDI_CHANNEL)
    sleep(0.5)

    note_off(TEST_NOTE, 0, MIDI_CHANNEL)
    sleep(0.5)
