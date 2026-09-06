from machine import UART, Pin
from time import sleep

# MIDI UART
midi = UART(
    0,
    baudrate=31250,
    tx=Pin(0)
)

# Onboard LED
led = Pin(18, Pin.OUT)

MIDI_CHANNEL = 1
TEST_NOTE = 60
TEST_VELOCITY = 100


def note_on(note, velocity=100, channel=1):
    status = 0x90 | ((channel - 1) & 0x0F)
    midi.write(bytes((status, note, velocity)))
    led.on()


def note_off(note, velocity=0, channel=1):
    status = 0x80 | ((channel - 1) & 0x0F)
    midi.write(bytes((status, note, velocity)))
    led.off()


while True:
    note_on(TEST_NOTE, TEST_VELOCITY, MIDI_CHANNEL)
    sleep(0.5)

    note_off(TEST_NOTE, 0, MIDI_CHANNEL)
    sleep(0.5)
